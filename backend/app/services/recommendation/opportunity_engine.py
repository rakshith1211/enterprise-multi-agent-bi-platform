from typing import List, Dict, Any
from app.schemas.recommendation import RecommendationItem

class OpportunityEngine:
    @staticmethod
    def detect_opportunities(analytics: Dict[str, Any], forecast: Dict[str, Any], rules: List[str]) -> List[RecommendationItem]:
        items = []
        
        # Rule 1: Increasing forecast trend opportunity
        forecast_trend = forecast.get("trend", "").lower()
        if forecast_trend == "increasing":
            items.append(RecommendationItem(
                title="Capitalize on Sales Growth Trend",
                type="Revenue Optimization",
                priority="High",
                business_impact="Capturing positive market demand projections will accelerate top-line revenue expansion.",
                confidence=0.92,
                reasoning="Calculated because forecast trend indicator is 'Increasing' with high statistical confidence.",
                affected_kpis=["revenue", "growth_rate"],
                affected_departments=["Sales", "Marketing"],
                estimated_benefits="Expected revenue growth uptick of 8% to 15% over the forecast period.",
                estimated_risks="Supply-chain capacity strains if customer demand outpaces inventory limits.",
                suggested_actions=[
                    "Increase advertising campaign spending across primary marketing channels.",
                    "Ensure adequate inventory procurement levels to support the sales peak."
                ]
            ))

        # Rule 2: High margin efficiency
        profit_margin = analytics.get("kpis", {}).get("profit_margin", 0.0)
        # Check standard rules
        high_margin_rule = any("margin" in r.lower() and "high" in r.lower() for r in rules)
        if profit_margin > 25.0 or high_margin_rule:
            items.append(RecommendationItem(
                title="Leverage High Profit Margin Thresholds",
                type="Pricing Optimization",
                priority="Medium",
                business_impact="Profit margins exceed target thresholds, indicating pricing power and efficiency.",
                confidence=0.85,
                reasoning=f"Triggered by analytics profit margin profile ({profit_margin}%) exceeding standard corporate margin limits.",
                affected_kpis=["profit_margin", "net_income"],
                affected_departments=["Finance", "Product Management"],
                estimated_benefits="Sustained profit margins and optimized product tier values.",
                estimated_risks="Competitor price undercut strategies if price ceiling is pushed too high.",
                suggested_actions=[
                    "Conduct customer value-tier studies to evaluate premium product upgrades.",
                    "Review pricing structures of lower-volume high-margin inventory items."
                ]
            ))

        return items
