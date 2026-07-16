import base64
import csv
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DocumentLoaderFactory:
    @staticmethod
    def load_document(file_type: str, content_base64: str = None, text_content: str = None) -> str:
        # Resolve text content if already provided
        if text_content:
            return text_content
            
        if not content_base64:
            raise ValueError("Base64 content or text content must be provided.")
            
        binary_data = base64.b64decode(content_base64)
        file_type = file_type.lower()
        
        try:
            if file_type == "txt" or file_type == "md":
                return binary_data.decode("utf-8", errors="ignore")
                
            elif file_type == "pdf":
                # Simulated text extraction from PDF binary stream bytes
                lines = []
                for chunk in binary_data.split(b"\n"):
                    cleaned = chunk.decode("utf-8", errors="ignore").strip()
                    if cleaned and not cleaned.startswith("%PDF"):
                        lines.append(cleaned)
                return " ".join(lines) if lines else "Simulated PDF textual corpus. Document metrics."
                
            elif file_type == "docx" or file_type == "pptx":
                # Fallback clean extraction
                return f"Simulated office XML extraction: {binary_data.decode('utf-8', errors='ignore')[:1000]}"
                
            elif file_type == "csv":
                decoded = binary_data.decode("utf-8", errors="ignore")
                reader = csv.reader(decoded.splitlines())
                rows = [", ".join(row) for row in reader]
                return "\n".join(rows)
                
            elif file_type == "json":
                decoded = binary_data.decode("utf-8", errors="ignore")
                data = json.loads(decoded)
                return json.dumps(data, indent=2)
                
            elif file_type == "sql":
                # Database schema details loader
                return f"Database Schema Definition Context: {binary_data.decode('utf-8', errors='ignore')}"
                
            elif file_type == "rule":
                # Business rules loader
                return f"Corporate Business Policy Rule Context: {binary_data.decode('utf-8', errors='ignore')}"
                
            else:
                return binary_data.decode("utf-8", errors="ignore")
                
        except Exception as e:
            logger.error(f"Loader error extracting file type {file_type}: {e}")
            return f"Error extracting document contents: {str(e)}"
