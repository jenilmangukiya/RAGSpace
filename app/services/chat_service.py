import json
from pymupdf.mupdf import pint_assign
from alembic.command import history
from app.schemas.chat import ChatMessage
from app.services.llm_service import LLMService
from app.services.search_service import SearchService


class ChatService:
    @staticmethod
    def chat(
        question: str,
        user_id: str,
        app_id: str,
        history: list[ChatMessage],
    ):
        query = question
        if history:
            query = LLMService.rewrite_query(question=question, history=history)

        search_result = SearchService.search(
            query=query,
            user_id=user_id,
            app_id=app_id,
        )

        if not search_result:
            return {
                "answer": (
                    "I could not find any relevant "
                    "information in the uploaded documents."
                ),
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

        return {
            "answer": answer,
            "sources": sources,
        }

    @staticmethod
    def stream_chat(
        question: str,
        history: list,
        user_id: str,
        app_id: str,
    ):
        query = question
        if history:
            query = LLMService.rewrite_query(question=question, history=history)

        search_result = SearchService.search(
            query=query,
            user_id=user_id,
            app_id=app_id,
        )

        if not search_result:
            return {
                "answer": (
                    "I could not find any relevant "
                    "information in the uploaded documents."
                ),
                "sources": [],
            }

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
            }
            for result in search_result[:5]
        ]

        # Stream answer tokens
        for token in LLMService.stream_answer(messages):
            yield (f"data: {json.dumps({'type': 'token', 'data': token})}\n\n")

        # Send sources
        yield (f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n")

        # Send done event
        yield (f"data: {json.dumps({'type': 'done'})}\n\n")
