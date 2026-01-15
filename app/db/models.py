from __future__ import annotations

from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime, ForeignKey)
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(32), default="pending")
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    link = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    author = relationship("User")
