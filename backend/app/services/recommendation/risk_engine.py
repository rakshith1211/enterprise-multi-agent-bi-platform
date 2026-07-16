from typing import List, Dict, Any
from app.schemas.recommendation import RecommendationItem

class RiskEngine:
    @staticmethod
    def evaluate_risks(analytics: Dict[str, Any], forecast: Dict[str, Any], rules: List[str]) -> List[RecommendationItem]:
        items = []

        # Rule 1: Decreasing forecast trend risk
        forecast_trend = forecast.get("trend", "").lower()
        if forecast_trend == "decreasing":
            items.append(RecommendationItem(
                title="Mitigate Projected Revenue Churn",
                type="Customer Retention",
                priority="High",
                business_impact="A downward forecast trend signals customer base contraction and pricing deterioration.",
                confidence=0.90,
                reasoning="Generated because forecast trend projections indicate a 'Decreasing' direction.",
                affected_kpis=["revenue", "customer_retention_rate"],
                affected_departments=["Customer Success", "Sales"],
                estimated_benefits="Stabilized recurring revenue pipelines and lowered customer acquisition costs.",
                estimated_risks="Increased promotional discounts could compress net income margins.",
                suggested_actions=[
                    "Launch target loyalty incentives for high-value customers showing signs of usage decline.",
                    "Deploy customer success representatives to audit accounts with expiring subscriptions."
                ]
            ))

        # Rule 2: High anomaly counts detected in analytics
        anomalies_count = len(analytics.get("outliers", []))
        if anomalies_count >= 2:
            items.append(RecommendationItem(
                title="Investigate Operational Anomaly Metrics",
                type="Risk Alerts",
                priority="High",
                business_impact="Multiple outliers in KPI metrics indicate system volatility, errors, or security breaches.",
                confidence=0.95,
                reasoning=f"Triggered by the detection of {anomalies_count} extreme outlier values in historical datasets.",
                affected_kpis=["data_quality_score", "operational_cost"],
                affected_departments=["IT", "Operations", "Audit"],
                estimated_benefits="Early threat containment and restored data pipeline integrity.",
                estimated_risks="Resource diversion to investigate false positive anomaly alerts.",
                suggested_actions=[
                    "Audit data logging integrations for outliers and anomalies timestamps.",
                    "Check server execution logs for API timeout exceptions or connection failures."
                ]
            ))

        return items
