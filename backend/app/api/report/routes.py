from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import io
import uuid

from app.db.session import get_db
from app.schemas.report import ReportRequest, ReportResponse, ReportHistoryResponse
from app.services.report_service import ReportService

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def generate_corporate_reports(schema: ReportRequest, db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    return await service.generate_report(schema)

@router.get("/download/{id}")
async def download_compiled_report(id: uuid.UUID, format: str = "pdf", db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    content, mime = await service.get_report_content(id, format)
    
    # Return binary stream response
    return StreamingResponse(
        io.BytesIO(content),
        media_type=mime,
        headers={"Content-Disposition": f"attachment; filename=report_{id}.{format}"}
    )

@router.get("/history", response_model=List[ReportHistoryResponse])
async def list_report_history(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    return await service.get_history(skip, limit)

@router.get("/templates")
def list_available_report_templates():
    return {
        "templates": [
            {"name": "Executive Report", "description": "High-level visual summary and recommendations layout."},
            {"name": "Financial Report", "description": "Structured grid metrics audit and balance statements."},
            {"name": "Sales Report", "description": "Categorical revenue summaries and growth projections."},
            {"name": "Operations Report", "description": "Data quality scores and IT anomaly alerts."},
            {"name": "Marketing Report", "description": "Conversion rates and customer lifecycle indicators."}
        ]
    }

@router.get("/health")
def check_reports_health():
    return {"status": "healthy", "service": "Enterprise Report Generation Agent"}
