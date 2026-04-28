from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)        # base, hrms, lms, hiring
    display_name = Column(String(100), nullable=False)           # Base, HRMS, LMS, Hiring

    # optional: relationship (not mandatory for now)
    menus = relationship("Menu", backref="module")
