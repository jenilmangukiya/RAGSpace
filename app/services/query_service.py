from app.services.llm_service import LLMService


class QueryService:

    DOCUMENT_LEVEL_KEYWORDS = [
        "what information",
        "what documents",
        "what do you know",
        "summarize",
        "overview",
        "what is this about",
        "what files",
    ]

    @classmethod
    def is_document_level_question(
        cls,
        question: str,
    ):
        return any(
            keyword in question.lower() for keyword in cls.DOCUMENT_LEVEL_KEYWORDS
        )

    @staticmethod
    def classify_query(question: str):
        if QueryService.is_document_level_question(question):
            return "document"

        return LLMService.classify_query(question)
