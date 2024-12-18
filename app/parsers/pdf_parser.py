from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = []
            
            # Process all pages at once
            for page in reader.pages:
                text.append(page.extract_text())
            
            return "\n".join(text)
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Error parsing PDF: {str(e)}")