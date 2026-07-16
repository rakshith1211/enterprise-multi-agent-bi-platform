import io
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class PDFGenerator:
    @staticmethod
    def generate(title: str, analytics: Dict[str, Any], forecast: Dict[str, Any], recommendations: Dict[str, Any]) -> bytes:
        if not HAS_REPORTLAB:
            logger.warning("reportlab is not installed. Generating simulated PDF binary stream.")
            buffer = io.BytesIO()
            buffer.write(b"%PDF-1.4\n")
            buffer.write(f"%% Title: {title}\n".encode("utf-8"))
            buffer.write(f"%% KPIs: {str(analytics.get('kpis'))}\n".encode("utf-8"))
            buffer.write(f"%% Forecast: {str(forecast.get('trend'))}\n".encode("utf-8"))
            return buffer.getvalue()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#2ca02c"),
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = styles["Normal"]

        story = []
        
        # Cover Page
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated Timestamp: Business Intelligence Suite Audit", body_style))
        story.append(Spacer(1, 40))

        # 1. Executive Summary
        story.append(Paragraph("1. Executive Summary", heading_style))
        story.append(Paragraph(
            "This document compiles executive metrics summaries, analytics values, time-series forecasting trend directions, "
            "and corresponding risk-mitigation or expansion recommendations compiled by the Business Intelligence Suite.",
            body_style
        ))
        story.append(Spacer(1, 15))

        # 2. KPI Summary
        story.append(Paragraph("2. KPI Dashboard", heading_style))
        kpi_data = [["KPI Metric Name", "Value"]]
        for k, v in analytics.get("kpis", {}).items():
            kpi_data.append([str(k), str(v)])
        
        if len(kpi_data) > 1:
            t = Table(kpi_data, colWidths=[200, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1f77b4")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No active KPIs found in analytics data payload.", body_style))
        story.append(Spacer(1, 15))

        # 3. Forecast Projections
        story.append(Paragraph("3. Forecasting Results", heading_style))
        trend = forecast.get("trend", "Flat")
        model = forecast.get("model_used", "ARIMA")
        story.append(Paragraph(f"Active Forecasting Model: {model}", body_style))
        story.append(Paragraph(f"Projected Metric Trend Direction: {trend}", body_style))
        story.append(Spacer(1, 15))

        # 4. Recommendations
        story.append(Paragraph("4. Prescriptive Recommendations", heading_style))
        recs = recommendations.get("recommendations", [])
        for r in recs:
            story.append(Paragraph(f"<b>[{r.get('priority', 'Low')}] {r.get('title', '')}</b>", body_style))
            story.append(Paragraph(f"Action: {', '.join(r.get('suggested_actions', []))}", body_style))
            story.append(Spacer(1, 5))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
