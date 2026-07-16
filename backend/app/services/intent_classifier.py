import re

class IntentClassifier:
    @staticmethod
    def classify(query: str) -> str:
        query_lower = query.lower()
        
        # Regex mappings for quick classification
        if any(w in query_lower for w in ["forecast", "predict", "trend next", "projection"]):
            return "forecast"
        elif any(w in query_lower for w in ["recommend", "suggest", "optimize", "best way"]):
            return "recommendation"
        elif any(w in query_lower for w in ["chart", "plot", "graph", "visualize"]):
            return "visualization"
        elif any(w in query_lower for w in ["report", "generate pdf", "summary sheet"]):
            return "report_generation"
        elif any(w in query_lower for w in ["tables", "columns", "schema"]):
            return "metadata_search"
        else:
            return "analytics"
