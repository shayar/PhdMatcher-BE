import os
import uuid
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
import boto3
from botocore.exceptions import ClientError
import PyPDF2
import docx
from app.core.config import settings
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.embedding_service = EmbeddingService()
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
            return False
        
        # Check file size (if possible)
        if hasattr(file.file, 'seek'):
            file.file.seek(0, 2)  # Seek to end
            size = file.file.tell()
            file.file.seek(0)  # Seek back to beginning
            
            if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                return False
        
        return True
    
    async def upload_resume(self, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """Upload resume file and extract text"""
        try:
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{user_id}_{uuid.uuid4()}{file_ext}"
            
            # Read file content
            content = await file.read()
            
            # Upload to S3
            s3_key = f"resumes/{unique_filename}"
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type
            )
            
            # Extract text
            text = self._extract_text_from_file(content, file_ext)
            
            # Generate embedding
            embedding = self.embedding_service.encode_text(text)
            
            return {
                "file_path": f"s3://{settings.S3_BUCKET_NAME}/{s3_key}",
                "extracted_text": text,
                "embedding": embedding
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")
        except Exception as e:
            logger.error(f"File processing error: {e}")
            raise HTTPException(status_code=500, detail="File processing failed")
    
    def _extract_text_from_file(self, content: bytes, file_ext: str) -> str:
        """Extract text from file content"""
        try:
            if file_ext.lower() == '.pdf':
                return self._extract_text_from_pdf(content)
            elif file_ext.lower() in ['.docx', '.doc']:
                return self._extract_text_from_docx(content)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return ""
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        import io
        pdf_file = io.BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        import io
        doc_file = io.BytesIO(content)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()