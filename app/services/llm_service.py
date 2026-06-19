from app.services.embedding_service import EmbeddingService
from app.schemas.chat import ChatMessage
from app.integrations.openai import OpenAIClient


class LLMService:
    @staticmethod
    def generate_answer(question: str, context: str, history: list[ChatMessage]):
        messages = LLMService.build_messages(
            question=question, context=context, history=history
        )

        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content

    @staticmethod
    def build_messages(question: str, context: str, history: list[ChatMessage]):
        messages = [
            {
                "role": "system",
                "content": """
                    You are an AI assistant with access to the user's uploaded documents.

                    When answering:
                    - Speak naturally.
                    - Do not mention embeddings, vectors, retrieval, searchable summaries, or document chunks.
                    - Act as if the uploaded documents are your knowledge source.
                    - If the user asks what information you have, summarize the available knowledge in a helpful way.
                    - If the uploaded documents contain relevant information, use it confidently.
                    - Only say you don't know when the information truly does not exist in the provided documents.
                """,
            },
        ]

        for msg in history[-10:]:
            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": (f"Context:\n{context}\n\n" f"Question:\n{question}"),
            }
        )

        return messages

    @staticmethod
    def stream_answer(messages):
        stream = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content

            if delta:
                yield delta

    @staticmethod
    def rewrite_query(
        question: str,
        history: list,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": """
                Rewrite the user's question into a standalone question.

                Use the conversation history to resolve:
                - pronouns
                - references
                - missing context

                Return ONLY the rewritten question.

                Examples:

                What is its revenue?
                → What is Google's revenue?

                Who founded it?
                → Who founded Google?
                """,
            }
        ]

        for msg in history[-10:]:
            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content.strip()

    @staticmethod
    def generate_document_summary(text: str):
        summary_source = text[:20000]

        messages = [
            {
                "role": "system",
                "content": """
        Create a searchable summary.

        Include:
        - Main topic
        - Key concepts
        - Important entities
        - Technologies
        - Important facts

        This summary will be used for document retrieval.
        """,
            },
            {
                "role": "user",
                "content": summary_source,
            },
        ]

        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
        )

        summary = response.choices[0].message.content.strip()

        summary_embedding: list[float] = EmbeddingService.create_embedding(summary)

        return {
            "summary": summary,
            "summary_embedding": summary_embedding,
        }

    @staticmethod
    def classify_query(question: str):
        messages = [
            {
                "role": "system",
                "content": """
                        Classify the user's query.

                        Return ONLY one word:

                        - "document"   → If the query is about the uploaded document.
                        - "chat"       → If the query is a casual question.
                    """,
            },
            {
                "role": "user",
                "content": question,
            },
        ]

        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content.strip()
