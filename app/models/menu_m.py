from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    route = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=True)
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    menu_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)

    # Self-referential relationship for parent-child hierarchy
    parent = relationship("Menu", remote_side=[id], backref="children")
    
    # Relationship with role rights
    role_rights = relationship("RoleRight", back_populates="menu", cascade="all, delete-orphan")
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)