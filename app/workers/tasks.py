from app.services.llm_service import LLMService
from app.models import App
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService
from app.services import chunk_service
from app.services.chunk_service import ChunkService
import logging

from app.db.session import create_db_session
from app.models.document import Document
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService


logger = logging.getLogger(__name__)


async def process_document(
    ctx,
    document_id: str,
):
    db = create_db_session()
    logger.info(f"Processing document: {document_id}")

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            return

        app = db.query(App).filter(App.id == document.app_id).first()

        document.status = "processing"
        db.commit()

        local_pdf_path = StorageService.download_document(document.storage_path)

        extracted_text: list[dict] = PDFService.extract_text(local_pdf_path)

        full_text = "\n\n".join(page["page_content"] for page in extracted_text)

        summary_and_embedding: dict = LLMService.generate_document_summary(full_text)

        QdrantService.upsert_chunks(
            chunks=[
                {
                    "page_number": "Summary",
                    "chunk_content": summary_and_embedding["summary"],
                }
            ],
            vectors=[summary_and_embedding["summary_embedding"]],
            user_id=app.user_id,
            app_id=app.id,
            document_id=document.id,
            document_name=document.file_name,
            type="document_summary",
        )

        all_chunks = []
        for page in extracted_text:
            chunks = ChunkService.chunk_text(page["page_content"])
            for chunk in chunks:
                all_chunks.append(
                    {
                        "page_number": page["page_number"],
                        "chunk_content": chunk,
                    }
                )

        vectors = []
        for chunk in all_chunks:
            vector = EmbeddingService.create_embedding(chunk["chunk_content"])
            vectors.append(vector)

        QdrantService.upsert_chunks(
            chunks=all_chunks,
            vectors=vectors,
            user_id=app.user_id,
            app_id=app.id,
            document_id=document.id,
            document_name=document.file_name,
            type="chunk",
        )

        document.status = "processed"

        db.commit()

        logger.info(f"Document processed: {document_id}")

    except Exception as e:
        logger.exception(e)

        document.status = "failed"
        document.error_message = str(e)

        db.commit()

    finally:
        db.close()

    return {
        "success": True,
        "document_id": document_id,
    }
