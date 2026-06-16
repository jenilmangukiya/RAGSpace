from app.services.llm_service import LLMService
from openai.resources.containers.files import content
from app.services.search_service import SearchService


class ChatService:
    @staticmethod
    def chat(
        question: str,
        user_id: str,
        app_id: str,
    ):
        search_result = SearchService.search(
            query=question,
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
            question=question,
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

        return {
            "answer": answer,
            "sources": sources,
        }
