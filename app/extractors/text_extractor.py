import os
import logging
from fastapi import UploadFile
import aiofiles
import docx
import PyPDF2
import io

logger = logging.getLogger(__name__)

class TextExtractor:
    async def extract_text(self, file: UploadFile) -> str:
        """Extract text from uploaded file"""
        try:
            # Save file temporarily
            file_path = await self._save_temp_file(file)
            
            # Extract text based on file type
            if file.filename.lower().endswith('.pdf'):
                text = self._extract_from_pdf(file_path)
            elif file.filename.lower().endswith('.docx'):
                text = self._extract_from_docx(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Cleanup
            os.remove(file_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file temporarily"""
        try:
            os.makedirs("temp", exist_ok=True)
            file_path = f"temp/{file.filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise 