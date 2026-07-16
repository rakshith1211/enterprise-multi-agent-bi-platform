import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.report import ReportHistory
from app.schemas.report import ReportRequest, ReportResponse
from app.db.repositories.report import ReportRepository
from app.services.report.pdf_generator import PDFGenerator
from app.services.report.docx_generator import DOCXGenerator
from app.services.report.pptx_generator import PPTXGenerator
from app.services.report.html_generator import HTMLGenerator
from app.services.connection_service import cache

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, db: AsyncSession):
        self.repo = ReportRepository(db)

    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        # Check cache
        cache_key = f"report:{hash(request.model_dump_json())}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("Serving report details from Redis cache.")
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return ReportResponse(**cached)

        # 1. Compile all formats
        pdf_bytes = PDFGenerator.generate(request.title, request.analytics_data, request.forecast_data, request.recommendations_data)
        docx_bytes = DOCXGenerator.generate(request.title, request.analytics_data, request.forecast_data, request.recommendations_data)
        pptx_bytes = PPTXGenerator.generate(request.title, request.analytics_data, request.forecast_data, request.recommendations_data)
        html_str = HTMLGenerator.generate_html(request.title, request.analytics_data, request.forecast_data, request.recommendations_data)
        md_str = HTMLGenerator.generate_markdown(request.title, request.analytics_data, request.forecast_data, request.recommendations_data)

        # 2. Persist in database
        report = ReportHistory(
            title=request.title,
            template=request.template,
            pdf_content=pdf_bytes,
            docx_content=docx_bytes,
            pptx_content=pptx_bytes,
            html_content=html_str,
            md_content=md_str
        )
        await self.repo.create(report)

        # 3. Format Response
        formats = ["pdf", "docx", "pptx", "html", "md"]
        download_urls = {fmt: f"/api/v1/reports/download/{report.id}?format={fmt}" for fmt in formats}
        
        response = ReportResponse(
            id=report.id,
            title=report.title,
            template_used=report.template,
            formats_available=formats,
            download_urls=download_urls,
            created_at=datetime.now(timezone.utc)
        )

        # 4. Cache report details (TTL 1 hour)
        resp_dict = response.model_dump()
        resp_dict["created_at"] = resp_dict["created_at"].isoformat()
        cache.set(cache_key, resp_dict, ttl=3600)

        return response

    async def get_report_content(self, report_id: uuid.UUID, format_type: str) -> tuple[bytes, str]:
        report = await self.repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report record not found")

        fmt = format_type.lower()
        if fmt == "pdf":
            return report.pdf_content, "application/pdf"
        elif fmt == "docx":
            return report.docx_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif fmt == "pptx":
            return report.pptx_content, "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif fmt == "html":
            return report.html_content.encode("utf-8"), "text/html"
        elif fmt == "md":
            return report.md_content.encode("utf-8"), "text/markdown"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported download report format: {format_type}")

    async def get_history(self, skip: int = 0, limit: int = 100) -> List[ReportHistory]:
        return await self.repo.list_history(skip, limit)
