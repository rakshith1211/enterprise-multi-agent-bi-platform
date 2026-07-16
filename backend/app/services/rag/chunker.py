from typing import List, Dict, Any
import re

class RAGChunker:
    @staticmethod
    def chunk_fixed(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        chunks = []
        words = text.split()
        step = chunk_size - overlap
        
        idx = 0
        chunk_num = 0
        while idx < len(words):
            slice_words = words[idx : idx + chunk_size]
            snippet = " ".join(slice_words)
            chunks.append({
                "chunk_index": chunk_num,
                "text": snippet,
                "strategy": "fixed-size",
                "length": len(snippet)
            })
            idx += step
            chunk_num += 1
            if len(slice_words) < chunk_size:
                break
                
        return chunks

    @staticmethod
    def chunk_recursive(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        # Splits on paragraphs first, then sentences, then words
        paragraphs = text.split("\n\n")
        chunks = []
        chunk_num = 0
        
        current_chunk = []
        current_len = 0
        
        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len <= chunk_size:
                current_chunk.append(para)
                current_len += para_len
            else:
                if current_chunk:
                    snippet = "\n\n".join(current_chunk)
                    chunks.append({
                        "chunk_index": chunk_num,
                        "text": snippet,
                        "strategy": "recursive",
                        "length": len(snippet)
                    })
                    chunk_num += 1
                current_chunk = [para]
                current_len = para_len
                
        if current_chunk:
            snippet = "\n\n".join(current_chunk)
            chunks.append({
                "chunk_index": chunk_num,
                "text": snippet,
                "strategy": "recursive",
                "length": len(snippet)
            })
            
        return chunks

    @staticmethod
    def chunk_semantic(text: str) -> List[Dict[str, Any]]:
        # Splits text on sentence boundaries (., !, ?) and groups in semantic triplets
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        chunk_num = 0
        
        # Group every 3 sentences
        for i in range(0, len(sentences), 3):
            triplet = " ".join(sentences[i : i + 3])
            chunks.append({
                "chunk_index": chunk_num,
                "text": triplet,
                "strategy": "semantic",
                "length": len(triplet)
            })
            chunk_num += 1
            
        return chunks

    @classmethod
    def chunk_document(cls, text: str, strategy: str = "recursive") -> List[Dict[str, Any]]:
        if strategy == "fixed":
            return cls.chunk_fixed(text)
        elif strategy == "semantic":
            return cls.chunk_semantic(text)
        else:
            return cls.chunk_recursive(text)
