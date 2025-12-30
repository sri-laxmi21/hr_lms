from fastapi import APIRouter, HTTPException
from app.services.test_report_service import save_test_report

router = APIRouter(
    prefix="/test-report",
    tags=["Test Reports"]
)


@router.post("/")
def create_test_report(report: dict):
    """
    Endpoint to save a Pytest or Schemathesis test report.
    """
    try:
        saved_report = save_test_report(report)
        return {
            "status": "success",
            "report_id": saved_report.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
