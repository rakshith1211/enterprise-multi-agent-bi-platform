import re
from typing import List, Dict, Any

class EntityExtractor:
    @staticmethod
    def extract_entities(query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        entities = {
            "metrics": [],
            "dimensions": [],
            "filters": []
        }

        # 1. Simple Keyword spotter for metrics
        if "revenue" in query_lower or "sales" in query_lower or "gmv" in query_lower:
            entities["metrics"].append("Revenue")
        if "cost" in query_lower or "expense" in query_lower:
            entities["metrics"].append("Cost")

        # 2. Extract dimensions
        if "region" in query_lower:
            entities["dimensions"].append("region")
        if "month" in query_lower or "monthly" in query_lower:
            entities["dimensions"].append("month")
        if "product" in query_lower:
            entities["dimensions"].append("product")

        # 3. Simple filters
        # Look for "region = South" or "region South" or "South region"
        regions = ["south", "north", "east", "west"]
        for r in regions:
            if r in query_lower:
                entities["filters"].append({
                    "column": "region",
                    "operator": "=",
                    "value": r.capitalize()
                })

        return entities
