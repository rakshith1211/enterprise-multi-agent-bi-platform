from typing import List, Dict, Any
from app.schemas.analytics import BusinessInsight, KPIsResult, TrendResult, AnomalyItem

class InsightGenerator:
    @staticmethod
    def generate_insights(kpis: KPIsResult, trends: Dict[str, TrendResult], anomalies: List[AnomalyItem]) -> List[BusinessInsight]:
        insights = []
        
        # 1. Net Margin insight
        if kpis.net_margin > 15.0:
            insights.append(BusinessInsight(
                title="Highly Profitable Operations",
                description=f"Operational net margins are strong at {kpis.net_margin}%. Profit conversion metrics are performing well.",
                priority="High",
                confidence=0.95,
                business_impact="Positive margin returns indicate high budget efficiency."
            ))
        elif kpis.net_margin < 5.0 and kpis.revenue > 0:
            insights.append(BusinessInsight(
                title="Profit Squeeze Warning",
                description=f"Net margins are low at {kpis.net_margin}%. Investigate supply chain or customer acquisition costs.",
                priority="High",
                confidence=0.90,
                business_impact="Critical threat to operational sustainability."
            ))

        # 2. Trends insight
        for col, t in trends.items():
            if t.direction == "Downward":
                insights.append(BusinessInsight(
                    title=f"Declining {col.capitalize()} Trend",
                    description=f"Detected contraction in {col}. The metric CAGR is moving downward at {t.cagr}%.",
                    priority="Medium",
                    confidence=0.88,
                    business_impact="Plan corrective actions or marketing adjustments."
                ))
            elif t.direction == "Upward" and t.cagr > 10.0:
                insights.append(BusinessInsight(
                    title=f"Growth Acceleration in {col.capitalize()}",
                    description=f"{col.capitalize()} is growing strongly with a CAGR of {t.cagr}%.",
                    priority="High",
                    confidence=0.92,
                    business_impact="Optimize inventory and staffing to support rising volume."
                ))

        # 3. Outlier insight
        if anomalies:
            insights.append(BusinessInsight(
                title=f"Anomalies Found in Data Metrics",
                description=f"Discovered {len(anomalies)} statistical anomalies. Values fell far outside Z-score thresholds.",
                priority="Medium",
                confidence=0.85,
                business_impact="Audit data logs or review temporary market conditions."
            ))

        # Fallback default insight
        if not insights:
            insights.append(BusinessInsight(
                title="Stable Metrics Flow",
                description="All KPIs and trend directions show standard historical values. Operational performance is flat.",
                priority="Low",
                confidence=0.99,
                business_impact="Maintain standard operational configurations."
            ))

        return insights
