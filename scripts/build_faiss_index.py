#!/usr/bin/env python3
"""
Build FAISS index from existing professor embeddings
"""
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings
from app.crud.professor import professor as crud_professor
from app.utils.vector_db import VectorDatabase

def build_faiss_index():
    """Build FAISS index from database"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Get all professors with embeddings
        professors = db.query(crud_professor.model).filter(
            crud_professor.model.embedding.isnot(None)
        ).all()
        
        print(f"Found {len(professors)} professors with embeddings")
        
        # Prepare data for FAISS
        professor_embeddings = []
        for prof in professors:
            if prof.embedding:
                embedding = json.loads(prof.embedding) if isinstance(prof.embedding, str) else prof.embedding
                professor_embeddings.append((prof.openalex_id, embedding))
        
        print(f"Processing {len(professor_embeddings)} embeddings...")
        
        # Build FAISS index
        vector_db = VectorDatabase()
        vector_db.rebuild_index(professor_embeddings)
        
        print("FAISS index built successfully!")
        
    except Exception as e:
        print(f"Error building FAISS index: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    build_faiss_index()