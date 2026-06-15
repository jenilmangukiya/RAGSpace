import logging

logger = logging.getLogger(__name__)


async def process_document(
    ctx,
    document_id: str,
):
    logger.info(f"Processing document: {document_id}")

    return {
        "success": True,
        "document_id": document_id,
    }
