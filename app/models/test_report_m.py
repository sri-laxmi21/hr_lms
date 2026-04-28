from sqlalchemy import JSON, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TestReport(Base):
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True) 
    created_by = Column(String(255), nullable=False,default="dev") 
    module_name = Column(String(255), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
    failures = Column(JSON, nullable=True)   # Store failures as a JSON string
    errors = Column(JSON, nullable=True)
    
    # ---------------- EXECUTION INFO ----------------
    execution_time = Column(String(50), nullable=False)
  
    environment = Column(String(50), default="local")

    # ---------------- TIMESTAMPS ----------------
    created_at = Column(DateTime(timezone=True), server_default=func.now())
