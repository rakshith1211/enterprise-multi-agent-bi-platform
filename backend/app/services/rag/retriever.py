from typing import Dict, Any, List
import re
from app.services.rag.vector_db import VectorStoreManager

class HybridRetriever:
    def __init__(self):
        self.store = VectorStoreManager()

    def _keyword_search_score(self, text: str, query: str) -> float:
        # Simple BM25 simulation: checks query token overlaps
        tokens = set(re.findall(r"\w+", query.lower()))
        if not tokens:
            return 0.0
        text_tokens = re.findall(r"\w+", text.lower())
        matches = sum(1 for t in tokens if t in text_tokens)
        return round(matches / len(tokens), 2)

    def retrieve(self, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # 1. Fetch from Vector Semantic Store
        semantic_results = self.store.query_semantic(query, limit=limit * 2, filters=filters)
        
        # 2. Apply Keyword/BM25 scores and Rerank
        reranked = []
        for res in semantic_results:
            kw_score = self._keyword_search_score(res["text"], query)
            # Combined score: 60% semantic + 40% keyword
            combined_score = round((res["score"] * 0.6) + (kw_score * 0.4), 2)
            
            node = dict(res)
            node["score"] = combined_score
            node["explainability"] = {
                "semantic_similarity": res["score"],
                "keyword_overlap": kw_score
            }
            reranked.append(node)
            
        # 3. Sort by combined score descending
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:limit]
