from typing import List, Dict, Any
from app.schemas.visualization import ChartRecommendation

class ChartRecommendationEngine:
    @staticmethod
    def recommend(columns: List[str], rows: List[Dict[str, Any]], preferred: str = None) -> tuple[ChartRecommendation, List[ChartRecommendation]]:
        cols_lower = [c.lower() for c in columns]
        
        # 1. Check if preferred is requested
        if preferred:
            primary = ChartRecommendation(
                chart_type=preferred,
                confidence=0.98,
                explanation=f"Selected user preferred chart type: {preferred}."
            )
            alt = ChartRecommendation(
                chart_type="Bar" if preferred != "Bar" else "Line",
                confidence=0.75,
                explanation="Alternative view configuration."
            )
            return primary, [alt]

        # 2. Heuristics based on fields cardinality and types
        # Check for time dimension
        has_time = any(t in cols_lower for t in ["month", "date", "year", "quarter", "time", "day"])
        
        # Identify numeric columns for Y axis
        numeric_cols = []
        if rows:
            first = rows[0]
            for col in columns:
                val = first.get(col)
                if isinstance(val, (int, float)) and not isinstance(val, bool) and col.lower() not in ["id", "port", "connection_id"]:
                    numeric_cols.append(col)

        # Recommendation logic
        if has_time and len(numeric_cols) >= 1:
            primary = ChartRecommendation(
                chart_type="Line",
                confidence=0.95,
                explanation="Line charts are optimal for showing continuous variables and value fluctuations over time dimensions."
            )
            alt = [
                ChartRecommendation(
                    chart_type="Bar",
                    confidence=0.80,
                    explanation="Bar charts provide categorical comparisons for discrete temporal buckets."
                ),
                ChartRecommendation(
                    chart_type="Area",
                    confidence=0.70,
                    explanation="Area charts highlight cumulative metric growth over time."
                )
            ]
        elif len(numeric_cols) >= 2:
            primary = ChartRecommendation(
                chart_type="Scatter",
                confidence=0.88,
                explanation="Scatter charts are recommended for displaying correlation trends and distributions between multiple numeric metrics."
            )
            alt = [
                ChartRecommendation(
                    chart_type="Bubble",
                    confidence=0.78,
                    explanation="Bubble charts map a third variable to marker size weights."
                ),
                ChartRecommendation(
                    chart_type="Heatmap",
                    confidence=0.65,
                    explanation="Heatmaps render density mappings across metrics matrices."
                )
            ]
        else:
            primary = ChartRecommendation(
                chart_type="Bar",
                confidence=0.90,
                explanation="Bar charts are recommended for comparing discrete values across categorical dimensions."
            )
            alt = [
                ChartRecommendation(
                    chart_type="Pie",
                    confidence=0.75,
                    explanation="Pie charts display composition ratios for low-cardinality values categories."
                ),
                ChartRecommendation(
                    chart_type="Donut",
                    confidence=0.72,
                    explanation="Donut charts display ratio values with a clean center space."
                )
            ]

        return primary, alt
