from pydantic import BaseModel
from typing import Optional, Dict, Any

class TestReportCreate(BaseModel):
    module_name: str
    total_tests: int
    passed: int
    failed: int

    failures: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, Any]] = None

    execution_time: str
    # framework: Optional[str] = "pytest"
    environment: Optional[str] = "local"
