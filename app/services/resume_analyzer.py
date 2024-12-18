from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from app.utils.text_processor import TextProcessor
import os
from dotenv import load_dotenv
import openai
import logging
import re
import uuid
import shutil

# Force reload of environment variables
load_dotenv(override=True)

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Configure OpenAI
openai.api_key = api_key

# Configure logger
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
            
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_api_key=self.api_key
        )
        self.text_processor = TextProcessor()
        
        # Create a directory for temporary Chroma DBs
        os.makedirs("temp_dbs", exist_ok=True)

    def analyze(self, text: str, options: list) -> dict:
        """Analyze resume text based on selected options"""
        try:
            session_id = str(uuid.uuid4())
            persist_directory = f"temp_dbs/{session_id}"
            
            logger.info(f"Starting new analysis session: {session_id}")
            logger.info(f"Selected options: {options}")
            
            cleaned_text = self.text_processor.clean_text(text)
            analysis = {}
            
            # Always extract contact info if selected
            if 'contact_info' in options:
                analysis['contact_info'] = self._extract_contact_info(cleaned_text)
            
            # Only create vector store if needed
            if set(options) - {'contact_info'}:
                try:
                    vectorstore = Chroma(
                        collection_name=f"resume_{session_id}",
                        embedding_function=self.embeddings,
                        persist_directory=persist_directory
                    )
                    
                    chunks = self.text_splitter.split_text(cleaned_text)
                    vectorstore.add_texts(chunks)
                    
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        chain_type="stuff",
                        retriever=vectorstore.as_retriever(
                            search_kwargs={"k": 3}
                        )
                    )
                    
                    # Extract only selected information
                    if 'personal_info' in options:
                        analysis['personal_info'] = self._extract_personal_info(qa_chain, cleaned_text)
                    if 'education' in options:
                        analysis['education'] = self._extract_education(qa_chain)
                    if 'experience' in options:
                        analysis['experience'] = self._extract_experience(qa_chain)
                    if 'skills' in options:
                        analysis['skills'] = self._extract_skills(qa_chain)
                    if 'summary' in options:
                        analysis['summary'] = self._generate_summary(qa_chain)
                    
                finally:
                    try:
                        vectorstore.delete_collection()
                        if os.path.exists(persist_directory):
                            shutil.rmtree(persist_directory)
                    except Exception as cleanup_error:
                        logger.error(f"Error during cleanup: {cleanup_error}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise
    
    def _extract_personal_info(self, qa_chain, text: str) -> dict:
        """Extract personal information"""
        try:
            logger.info("Starting personal info extraction")
            
            # More specific prompts for name extraction
            name_query = """
            What is the person's full name from this resume? 
            Look for:
            1. Name at the top/header of the resume
            2. Name after 'Name:' or similar labels
            3. Name in contact/personal information section
            Return ONLY the name, nothing else. If no name is found, return 'Not found'.
            """
            
            location_query = """
            What is the person's current location/address from this resume?
            Look for:
            1. Address in contact information
            2. City and state/country
            3. Location mentioned with current position
            Return ONLY the location, nothing else. If no location is found, return 'Not found'.
            """
            
            # Get responses with retries
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    name_response = qa_chain.run(name_query).strip()
                    location_response = qa_chain.run(location_query).strip()
                    
                    logger.info(f"Name extraction response (attempt {attempt + 1}): {name_response}")
                    logger.info(f"Location extraction response (attempt {attempt + 1}): {location_response}")
                    
                    # Validate responses
                    if name_response and name_response.lower() != "not found":
                        break
                except Exception as retry_error:
                    logger.warning(f"Retry {attempt + 1} failed: {retry_error}")
                    if attempt == max_retries - 1:
                        raise
            
            # Clean up responses
            name = name_response if name_response and name_response.lower() != "not found" else "Not found"
            location = location_response if location_response and location_response.lower() != "not found" else "Not found"
            
            result = {
                "name": name,
                "location": location
            }
            
            logger.info(f"Final personal info: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting personal info: {str(e)}")
            return {
                "name": "Error extracting name",
                "location": "Error extracting location"
            }
    
    def _extract_contact_info(self, text: str) -> dict:
        """Extract contact information using multiple methods"""
        try:
            logger.debug(f"Extracting contact info from text: {text[:200]}...")
            
            # First try regex through TextProcessor
            contact_info = self.text_processor.extract_contact_info(text)
            logger.info(f"Initial contact info from regex: {contact_info}")
            
            # If email is missing, try additional methods
            if not contact_info.get('email'):
                # Try direct pattern matching
                email_patterns = [
                    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
                    r'[A-Za-z0-9._]+@outlook\.com',
                    r'[A-Za-z]+[0-9]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
                ]
                
                for pattern in email_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        contact_info['email'] = matches[0]
                        logger.info(f"Found email with additional pattern: {matches[0]}")
                        break
                
                # If still not found, try LLM
                if not contact_info.get('email'):
                    email_query = """What is the email address in this text? 
                    Look for patterns like xxx@xxx.xxx or anything containing @ symbol.
                    Return only the email address without any additional text."""
                    
                    email_response = self.llm.predict(email_query + "\n\nText: " + text)
                    if email_response and '@' in email_response:
                        email = email_response.strip()
                        # Clean up any extra text around the email
                        email = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', email)
                        if email:
                            contact_info['email'] = email.group(0)
                            logger.info(f"Found email with LLM: {email.group(0)}")
            
            # Ensure we have all fields even if empty
            result = {
                "email": contact_info.get('email', "Not found"),
                "phone": contact_info.get('phone', "Not found"),
                "linkedin": contact_info.get('linkedin', "Not found")
            }
            
            logger.info(f"Final contact info: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")
            return {
                "email": "Error extracting email",
                "phone": "Error extracting phone",
                "linkedin": "Error extracting LinkedIn"
            }
    
    def _extract_education(self, qa_chain) -> list:
        """Extract education information"""
        query = """Extract all education information including:
        - Degree/Certificate name
        - Institution name
        - Graduation year
        - GPA (if mentioned)
        - Major/Specialization
        Please format as a list of educational experiences."""
        
        response = qa_chain.run(query)
        return response
    
    def _extract_experience(self, qa_chain) -> list:
        """Extract work experience"""
        query = """Extract all work experiences including:
        - Company name
        - Position/Title
        - Duration (start and end dates)
        - Key responsibilities and achievements
        Please format as a chronological list, starting with the most recent."""
        
        response = qa_chain.run(query)
        return response
    
    def _extract_skills(self, qa_chain) -> dict:
        """Extract skills categorized"""
        query = """Categorize the skills mentioned in the resume into:
        - Technical Skills
        - Soft Skills
        - Languages
        - Tools/Software
        - Certifications
        Please provide them as separate categories."""
        
        response = qa_chain.run(query)
        return response
    
    def _extract_keywords(self, qa_chain) -> list:
        """Extract important keywords"""
        query = """Extract the most important keywords from the resume that are relevant for:
        - Job search
        - Industry relevance
        - Technical expertise
        Please provide them as a list of keywords."""
        
        response = qa_chain.run(query)
        return response
    
    def _generate_summary(self, qa_chain) -> str:
        """Generate a professional summary"""
        query = """Generate a concise professional summary that includes:
        - Years of experience
        - Key expertise areas
        - Major achievements
        - Career highlights
        Limit to 3-4 sentences."""
        
        response = qa_chain.run(query)
        return response