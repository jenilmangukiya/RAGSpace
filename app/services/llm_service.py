from app.schemas.chat import ChatMessage
from app.integrations.openai import OpenAIClient


class LLMService:
    @staticmethod
    def generate_answer(question: str, context: str, history: list[ChatMessage]):
        messages = [
            {
                "role": "system",
                "content": """
                    You are a helpful assistant.

                    Answer ONLY using the provided context.

                    If the answer is not present in the context, say:
                    "I could not find that information in the uploaded documents."

                    Maintain the conversation history to understand context.
                """,
            },
        ]

        for msg in history[-10:]:
            messages.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": (f"Context:\n{context}\n\n" f"Question:\n{question}"),
            }
        )

        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )

        return response.choices[0].message.content

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
                    "role": msg.role,
                    "content": msg.content,
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
