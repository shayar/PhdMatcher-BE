import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.professor import professor as crud_professor
from app.crud.institution import institution as crud_institution
from app.models.professor import Professor
from app.models.institution import Institution
from app.services.embedding_service import EmbeddingService
from app.utils.vector_db import VectorDatabase
import logging

logger = logging.getLogger(__name__)

class OpenAlexService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.OPENALEX_API_URL
        self.email = settings.OPENALEX_API_EMAIL
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDatabase()
    
    async def sync_professors_by_institution(self, institution_ror: str) -> Dict[str, int]:
        """Sync professors from a specific institution"""
        url = f"{self.base_url}/authors"
        params = {
            "filter": f"last_known_institution.ror:{institution_ror}",
            "per_page": 200,
            "select": "id,display_name,last_known_institution,works_count,cited_by_count,summary_stats,concepts,orcid,homepage",
            "mailto": self.email
        }
        
        synced_count = 0
        updated_count = 0
        
        async with aiohttp.ClientSession() as session:
            cursor = "*"
            
            while cursor:
                if cursor != "*":
                    params["cursor"] = cursor
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"OpenAlex API error: {response.status}")
                        break
                    
                    data = await response.json()
                    
                    for author_data in data.get("results", []):
                        try:
                            result = await self._process_author(author_data)
                            if result == "created":
                                synced_count += 1
                            elif result == "updated":
                                updated_count += 1
                        except Exception as e:
                            logger.error(f"Error processing author {author_data.get('id')}: {e}")
                    
                    # Check for next page
                    meta = data.get("meta", {})
                    cursor = meta.get("next_cursor")
                    
                    if not cursor:
                        break
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
        
        # Save vector database
        self.vector_db.save_index()
        
        return {
            "synced_count": synced_count,
            "updated_count": updated_count
        }
    
    async def _process_author(self, author_data: Dict[str, Any]) -> str:
        """Process individual author data"""
        openalex_id = author_data["id"].replace("https://openalex.org/", "")
        
        # Check if professor already exists
        existing_prof = crud_professor.get_by_openalex_id(
            self.db, openalex_id=openalex_id
        )
        
        # Extract institution data
        institution_data = author_data.get("last_known_institution", {})
        institution_id = None
        if institution_data:
            institution_id = institution_data["id"].replace("https://openalex.org/", "")
            await self._process_institution(institution_data)
        
        # Prepare professor data
        concepts = author_data.get("concepts", [])[:10]  # Top 10 concepts
        
        # Create research summary
        research_summary = self._create_research_summary(author_data)
        
        # Generate embedding
        embedding = self.embedding_service.encode_text(research_summary)
        
        professor_data = {
            "openalex_id": openalex_id,
            "name": author_data["display_name"],
            "display_name": author_data["display_name"],
            "institution_id": institution_id,
            "works_count": author_data.get("works_count", 0),
            "cited_by_count": author_data.get("cited_by_count", 0),
            "concepts": concepts,
            "research_summary": research_summary,
            "orcid": author_data.get("orcid"),
            "homepage_url": author_data.get("homepage"),
            "embedding": embedding
        }
        
        # Extract h-index and i10-index from summary_stats
        summary_stats = author_data.get("summary_stats", {})
        professor_data["h_index"] = summary_stats.get("h_index", 0)
        professor_data["i10_index"] = summary_stats.get("i10_index", 0)
        
        if existing_prof:
            # Update existing professor
            for key, value in professor_data.items():
                if key != "openalex_id":  # Don't update primary key
                    setattr(existing_prof, key, value)
            self.db.commit()
            
            # Update vector database
            self.vector_db.add_embedding(openalex_id, embedding)
            
            return "updated"
        else:
            # Create new professor
            new_prof = Professor(**professor_data)
            self.db.add(new_prof)
            self.db.commit()
            
            # Add to vector database
            self.vector_db.add_embedding(openalex_id, embedding)
            
            return "created"
    
    async def _process_institution(self, institution_data: Dict[str, Any]):
        """Process institution data"""
        if not institution_data:
            return
        
        openalex_id = institution_data["id"].replace("https://openalex.org/", "")
        
        # Check if institution exists
        existing_inst = crud_institution.get_by_openalex_id(
            self.db, openalex_id=openalex_id
        )
        
        if not existing_inst:
            # Fetch detailed institution data
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/institutions/{openalex_id}"
                params = {"mailto": self.email}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        detailed_data = await response.json()
                        
                        inst_data = {
                            "openalex_id": openalex_id,
                            "name": detailed_data.get("display_name", ""),
                            "display_name": detailed_data.get("display_name", ""),
                            "country_code": detailed_data.get("country_code", ""),
                            "country": detailed_data.get("country", ""),
                            "type": detailed_data.get("type", ""),
                            "homepage_url": detailed_data.get("homepage_url", ""),
                            "ror_id": detailed_data.get("ror", ""),
                            "works_count": detailed_data.get("works_count", 0),
                        }
                        
                        # Extract location data
                        geo = detailed_data.get("geo", {})
                        if geo:
                            inst_data["city"] = geo.get("city")
                            inst_data["region"] = geo.get("region")
                            inst_data["geo"] = {
                                "latitude": geo.get("latitude"),
                                "longitude": geo.get("longitude")
                            }
                        
                        new_inst = Institution(**inst_data)
                        self.db.add(new_inst)
                        self.db.commit()
    
    def _create_research_summary(self, author_data: Dict[str, Any]) -> str:
        """Create a research summary from author data"""
        summary_parts = []
        
        # Add display name
        if author_data.get("display_name"):
            summary_parts.append(author_data["display_name"])
        
        # Add top concepts
        concepts = author_data.get("concepts", [])[:5]  # Top 5 concepts
        if concepts:
            concept_names = [c.get("display_name", "") for c in concepts]
            summary_parts.append("Research areas: " + ", ".join(concept_names))
        
        # Add institution
        institution = author_data.get("last_known_institution", {})
        if institution:
            summary_parts.append(f"Institution: {institution.get('display_name', '')}")
        
        return ". ".join(summary_parts)