from app.integrations.reranker import reranker


class RerankerService:
    @staticmethod
    def rerank(query: str, search_results: list, top_k: int = 5):
        pairs = [
            (
                query,
                result.payload["text"],
            )
            for result in search_results
        ]

        scores = reranker.predict(pairs)

        ranked = sorted(
            zip(search_results, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return [result for result, score in ranked[:top_k]]
