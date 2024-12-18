from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from app.utils.text_processor import TextProcessor
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        # Initialize components
        self.text_processor = TextProcessor()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            openai_api_key=self.api_key
        )

    def analyze(self, text: str) -> dict:
        """Analyze resume text"""
        try:
            # Extract contact info first (using regex)
            contact_info = self.text_processor.extract_contact_info(text)
            
            # Clean and prepare text for RAG
            cleaned_text = self.text_processor.clean_text(text)
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create vector store and QA chain
            vectorstore = Chroma.from_texts(chunks, self.embeddings)
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever()
            )
            
            # Extract information using RAG
            return {
                "contact_info": contact_info,
                "personal_info": self._extract_personal_info(qa_chain),
                "education": self._extract_education(qa_chain),
                "experience": self._extract_experience(qa_chain),
                "skills": self._extract_skills(qa_chain),
                "summary": self._generate_summary(qa_chain)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise

    def _extract_personal_info(self, qa_chain) -> dict:
        query = "What is the person's full name and current location/address?"
        response = qa_chain.run(query)
        return {"name": response}

    def _extract_education(self, qa_chain) -> str:
        query = """Extract all education information including:
        - Degree/Certificate name
        - Institution name
        - Graduation year
        - GPA (if mentioned)
        Format as a clear list."""
        return qa_chain.run(query)

    def _extract_experience(self, qa_chain) -> str:
        query = """Extract work experience including:
        - Company names
        - Positions/Titles
        - Duration
        - Key responsibilities
        Format as a chronological list."""
        return qa_chain.run(query)

    def _extract_skills(self, qa_chain) -> str:
        query = """List all skills mentioned, categorized into:
        - Technical Skills
        - Soft Skills
        - Tools/Software"""
        return qa_chain.run(query)

    def _generate_summary(self, qa_chain) -> str:
        query = """Generate a brief professional summary highlighting:
        - Years of experience
        - Key expertise
        - Major achievements
        Limit to 3-4 sentences."""
        return qa_chain.run(query) 