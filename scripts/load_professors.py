#!/usr/bin/env python3
"""
Load professors from OpenAlex API for specific institutions
"""
import asyncio
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings
from app.services.openalex_service import OpenAlexService

async def load_professors(institution_ror: str):
    """Load professors for a specific institution"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        openalex_service = OpenAlexService(db)
        result = await openalex_service.sync_professors_by_institution(institution_ror)
        
        print(f"Successfully loaded professors:")
        print(f"  Synced: {result['synced_count']}")
        print(f"  Updated: {result['updated_count']}")
        
    except Exception as e:
        print(f"Error loading professors: {e}")
    finally:
        db.close()

async def main():
    if len(sys.argv) != 2:
        print("Usage: python load_professors.py <institution_ror_id>")
        print("Example: python load_professors.py 00f54p054")  # Stanford
        sys.exit(1)
    
    institution_ror = sys.argv[1]
    await load_professors(institution_ror)

if __name__ == "__main__":
    asyncio.run(main())