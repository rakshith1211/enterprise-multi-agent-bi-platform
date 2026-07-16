from typing import Dict, Any

class HTMLGenerator:
    @staticmethod
    def generate_html(title: str, analytics: Dict[str, Any], forecast: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        kpis_html = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in analytics.get("kpis", {}).items()])
        recs_html = "".join([
            f"<li><b>[{r.get('priority')}] {r.get('title')}</b>: {', '.join(r.get('suggested_actions', []))}</li>" 
            for r in recommendations.get("recommendations", [])
        ])

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #1f77b4; }}
        h2 {{ color: #2ca02c; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><i>Generated Timestamp: Business Intelligence Report Session Audit</i></p>
    
    <h2>1. Executive Summary</h2>
    <p>Compiled report details performance levels and forecasting projections across active metrics dimensions.</p>
    
    <h2>2. KPI Dashboard</h2>
    <table>
        <thead>
            <tr><th>Metric</th><th>Value</th></tr>
        </thead>
        <tbody>
            {kpis_html if kpis_html else "<tr><td colspan='2'>No KPIs found.</td></tr>"}
        </tbody>
    </table>

    <h2>3. Forecasting Results</h2>
    <p><b>Projected Trend:</b> {forecast.get("trend", "Flat")}</p>
    <p><b>Analysis Model:</b> {forecast.get("model_used", "ARIMA")}</p>

    <h2>4. Actionable Recommendations</h2>
    <ul>
        {recs_html if recs_html else "<li>No recommendations compiled.</li>"}
    </ul>
</body>
</html>
"""

    @staticmethod
    def generate_markdown(title: str, analytics: Dict[str, Any], forecast: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        kpis_md = "\n".join([f"| {k} | {v} |" for k, v in analytics.get("kpis", {}).items()])
        recs_md = "\n".join([
            f"- **[{r.get('priority')}] {r.get('title')}**: {', '.join(r.get('suggested_actions', []))}"
            for r in recommendations.get("recommendations", [])
        ])

        return f"""# {title}

*Generated Timestamp: BI Audit Session*

## 1. Executive Summary
Compiled report details performance levels and forecasting projections across active metrics dimensions.

## 2. KPI Dashboard
| Metric | Value |
| :--- | :--- |
{kpis_md if kpis_md else "| No KPIs found | - |"}

## 3. Forecasting Results
- **Projected Trend:** {forecast.get("trend", "Flat")}
- **Analysis Model:** {forecast.get("model_used", "ARIMA")}

## 4. Actionable Recommendations
{recs_md if recs_md else "- No recommendations compiled."}
"""
