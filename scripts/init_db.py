#!/usr/bin/env python3
"""
Initialize the database with tables and sample data
"""
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.models import user, professor, institution

def init_db():
    """Initialize database"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()