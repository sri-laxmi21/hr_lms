import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace
from collections import defaultdict
from dotenv import load_dotenv
import time

from app.main import app
from app.database import Base, engine, SessionLocal, get_db
from app.dependencies import get_current_user
from app.models.test_report_m import TestReport

load_dotenv(".env.test")

# ======================================================
# TEST RESULT STORAGE (IN-MEMORY)
# ======================================================
TEST_RESULTS = defaultdict(lambda: {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "failures": [],
    "errors": []
})

START_TIME = time.time()

# ======================================================
# DATABASE SETUP (CREATE TABLES ONCE)
# ======================================================
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create tables once.
    DO NOT drop tables → test_reports must persist.
    """
    Base.metadata.create_all(bind=engine)
    yield

# ======================================================
# DB SESSION WITH FULL ROLLBACK (CRITICAL)
# ======================================================
@pytest.fixture(scope="function")
def db_session():
    """
    Any data created in tests is rolled back,
    EVEN IF API internally calls commit().
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# ======================================================
# FAKE AUTH USER
# ======================================================
def fake_super_admin_user():
    return SimpleNamespace(
        id=1,
        first_name="Test",
        last_name="Admin",
        email="admin@test.com",
        role_id=1,
        role=SimpleNamespace(id=1, name="super_admin"),
        organization_id=1,
        is_active=True
    )

# ======================================================
# FASTAPI CLIENT
# ======================================================
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: fake_super_admin_user()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

# ======================================================
# PYTEST HOOKS – COLLECT RESULTS
# ======================================================
def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    module = report.nodeid.split("::")[0].split("/")[-1]
    data = TEST_RESULTS[module]

    data["total_tests"] += 1

    if report.passed:
        data["passed"] += 1
    else:
        data["failed"] += 1
        data["failures"].append(str(report.longrepr)[:1000])

# ======================================================
# SAVE TEST RESULTS (NO ROLLBACK)
# ======================================================
def pytest_sessionfinish(session, exitstatus):
    """
    Save test results permanently.
    Uses a SEPARATE DB session.
    """
    execution_time = f"{round(time.time() - START_TIME, 2)}s"

    report_db = SessionLocal()
    try:
        for module, data in TEST_RESULTS.items():
            report_db.add(
                TestReport(
                    module_name=module,
                    total_tests=data["total_tests"],
                    passed=data["passed"],
                    failed=data["failed"],
                    failures=data["failures"] or None,
                    errors=data["errors"] or None,
                    execution_time=execution_time
                )
            )
        report_db.commit()
    finally:
        report_db.close()
