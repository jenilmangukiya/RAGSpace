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

        document.status = "processing"
        db.commit()

        local_pdf_path = StorageService.download_document(document.storage_path)

        extracted_text = PDFService.extract_text(local_pdf_path)

        document.extracted_text = extracted_text
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
