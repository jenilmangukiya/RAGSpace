from app.services.conversation_service import ConversationService
from sqlalchemy.orm import Session
from app.services import conversation_service
import asyncio
import json
import time
from pymupdf.mupdf import pint_assign
from alembic.command import history
from app.schemas.chat import ChatMessage
from app.services.llm_service import LLMService
from app.services.search_service import SearchService


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def chat(
        self,
        question: str,
        user_id: str,
        app_id: str,
        conversation_id: str,
    ):
        conversation_service_instance = ConversationService(self.db)

        # Get chat History from DB
        db_history = conversation_service_instance.get_conversation_latest_history(
            conversation_id, user_id
        )
        history = [
            {"role": message.role, "content": message.content} for message in db_history
        ]

        query = question
        if history:
            query = LLMService.rewrite_query(question=question, history=history)

        search_result = SearchService.search(
            query=query,
            user_id=user_id,
            app_id=app_id,
        )

        if not search_result:
            error_message = (
                "I could not find any relevant information in the uploaded documents."
            )

            conversation_service_instance.save_chat_exchange(
                assistant_message=error_message,
                conversation_id=conversation_id,
                user_message=question,
            )

            return {
                "answer": error_message,
                "sources": [],
            }

        context = "\n\n".join(result["text"] for result in search_result[:5])

        answer = LLMService.generate_answer(
            question=question, context=context, history=history
        )

        sources = [
            {
                "document_id": result["document_id"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
            }
            for result in search_result[:5]
        ]

        conversation_service_instance.save_chat_exchange(
            assistant_message=answer,
            conversation_id=conversation_id,
            user_message=question,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    def stream_chat(
        self,
        question: str,
        user_id: str,
        app_id: str,
        conversation_id: str,
    ):
        conversation_service_instance = ConversationService(self.db)

        # Get chat History from DB
        db_history = conversation_service_instance.get_conversation_latest_history(
            conversation_id, user_id
        )
        history = [
            {"role": message.role, "content": message.content} for message in db_history
        ]

        query = question
        if history:
            query = LLMService.rewrite_query(question=question, history=history)

        search_result = SearchService.search(
            query=query,
            user_id=user_id,
            app_id=app_id,
        )

        if not search_result:
            error_message = (
                "I could not find any relevant information in the uploaded documents."
            )
            conversation_service_instance.save_chat_exchange(
                assistant_message=error_message,
                conversation_id=conversation_id,
                user_message=question,
            )

            yield (f"data: {json.dumps({'type': 'token', 'data': error_message})}\n\n")
            time.sleep(0.01)
            yield (f"data: {json.dumps({'type': 'done'})}\n\n")
            return

        context = "\n\n".join(result["text"] for result in search_result[:5])

        messages = LLMService.build_messages(
            question=question,
            history=history,
            context=context,
        )
        sources = [
            {
                "document_id": result["document_id"],
                "chunk_index": result["chunk_index"],
                "score": result["score"],
                "page_number": result["page_number"],
                "document_name": result.get("document_name"),
            }
            for result in search_result[:5]
        ]

        full_answer = ""
        try:
            # Stream answer tokens
            for token in LLMService.stream_answer(messages):
                full_answer += token
                yield (f"data: {json.dumps({'type': 'token', 'data': token})}\n\n")
        finally:
            conversation_service_instance.save_chat_exchange(
                assistant_message=full_answer,
                conversation_id=conversation_id,
                user_message=question,
            )

        # Send sources
        yield (f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n")

        # Send done event
        yield (f"data: {json.dumps({'type': 'done'})}\n\n")
