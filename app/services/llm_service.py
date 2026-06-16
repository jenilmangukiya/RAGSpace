from app.integrations.openai import OpenAIClient


class LLMService:
    @staticmethod
    def generate_answer(question: str, context: str):
        response = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant.\n\n"
                        "Answer ONLY using the provided context.\n"
                        "If the answer is not present in the context, "
                        "say: 'I could not find that information in the uploaded documents.'"
                    ),
                },
                {
                    "role": "user",
                    "content": (f"Context:\n{context}\n\n" f"Question:\n{question}"),
                },
            ],
            temperature=0,
        )

        return response.choices[0].message.content
