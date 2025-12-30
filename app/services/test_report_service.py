import json
import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.test_report_m import TestReport


# ======================================================
# PARSE SCHEMATHESIS REPORT
# ======================================================
def parse_schemathesis_report(report_path: str) -> dict:
    with open(report_path, "r") as f:
        data = json.load(f)

    checks = data.get("checks", [])

    total_tests = len(checks)
    passed = len([c for c in checks if c.get("status") == "success"])
    failed = total_tests - passed

    failures = [
        {
            "name": c.get("name"),
            "message": c.get("message"),
            "status": c.get("status")
        }
        for c in checks
        if c.get("status") != "success"
    ]

    return {
        "schemathesis": {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "failures": failures,
            "errors": []
        }
    }


# ======================================================
# SAVE TEST REPORT
# ======================================================
def save_test_report(report_dict: dict):
    start_time = time.time()
    db = SessionLocal()

    try:
        for module_name, module_results in report_dict.items():
            test_report = TestReport(
                module_name=module_name,
                total_tests=module_results.get("total_tests", 0),
                passed=module_results.get("passed", 0),
                failed=module_results.get("failed", 0),
                failures=module_results.get("failures"),
                errors=module_results.get("errors"),
                execution_time=f"{round(time.time() - start_time, 2)}s"
            )

            db.add(test_report)

        db.commit()
        print("✅ Test report saved successfully")

    except Exception as e:
        db.rollback()
        print("❌ DB Error while saving test report:", e)
        raise

    finally:
        db.close()
