import logging
from fastapi import UploadFile
import os
import aiofiles
from app.services.resume_analyzer import ResumeAnalyzer
from app.extractors.text_extractor import TextExtractor

logger = logging.getLogger(__name__)

class ResumeService:
    def __init__(self):
        self.resume_analyzer = ResumeAnalyzer()
        self.text_extractor = TextExtractor()

    async def process_resume(self, file: UploadFile, selected_options: list) -> dict:
        """Process resume file and extract information"""
        try:
            logger.info(f"Processing resume: {file.filename}")
            logger.info(f"Selected options: {selected_options}")
            
            # Extract text from file
            text = await self.text_extractor.extract_text(file)
            logger.info(f"Extracted text length: {len(text)}")
            
            # Analyze text with selected options
            analysis = self.resume_analyzer.analyze(text, selected_options)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
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