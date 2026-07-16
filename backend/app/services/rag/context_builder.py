from typing import Dict, Any, List
from app.schemas.rag import CitationNode

class ContextBuilder:
    @staticmethod
    def build_prompt_context(matches: List[Dict[str, Any]]) -> str:
        if not matches:
            return "No matching domain documentation context was found in the RAG Knowledge Base."
            
        context_parts = []
        context_parts.append("Below are the relevant business documents and domain contexts extracted from the corporate repository:\n")
        
        for idx, match in enumerate(matches):
            doc_name = match["metadata"].get("document_name", "Unknown Document")
            chunk_idx = match["metadata"].get("chunk_index", 0)
            author = match["metadata"].get("author", "system")
            section = match["metadata"].get("section", "General")
            
            context_parts.append(
                f"[Source {idx+1}: {doc_name} | Section: {section} | Author: {author} | Chunk ID: {chunk_idx}]\n"
                f"{match['text']}\n"
            )
            
        return "\n".join(context_parts)

    @staticmethod
    def extract_citations(matches: List[Dict[str, Any]]) -> List[CitationNode]:
        citations = []
        for match in matches:
            citations.append(CitationNode(
                document_name=match["metadata"].get("document_name", "Unknown"),
                chunk_index=int(match["metadata"].get("chunk_index", 0)),
                matched_text=match["text"][:200] + "...",
                score=match["score"],
                metadata=match["metadata"]
            ))
        return citations
