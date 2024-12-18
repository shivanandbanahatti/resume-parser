# Resume Parser
An AI-powered resume parsing application that extracts and analyzes information from PDF and DOCX resumes.
## Features
- Extract personal information, contact details, education, experience, skills, and summary
 Support for PDF and DOCX file formats
 Selective information extraction
 Real-time processing with progress indication
 Download parsed results as JSON
 Session storage for parsed results
## Tech Stack
- Backend: FastAPI, Python
 Frontend: HTML, CSS, JavaScript
 AI/ML: OpenAI GPT-3.5, HuggingFace Sentence Transformers
 Document Processing: PyPDF2, python-docx
## Setup
1. Clone the repository:
bash
git clone https://github.com/yourusername/resume-parser.git
cd resume-parser

2. Create a virtual environment and install dependencies:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Create a `.env` file in the project root and add your OpenAI API key:
OPENAI_API_KEY=your_api_key_here

4. Run the application:
bash
uvicorn app.main:app --reload

5. Open your browser and navigate to:
http://localhost:8000

## Usage

1. Select the information you want to extract
2. Upload a resume file (PDF or DOCX)
3. Wait for the analysis to complete
4. View and download the parsed results

## Project Structure
project_root/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── services/
│ │ ├── init.py
│ │ ├── resume_analyzer.py
│ │ └── resume_service.py
│ ├── extractors/
│ │ ├── init.py
│ │ └── text_extractor.py
│ └── utils/
│ ├── init.py
│ ├── cleanup.py
│ └── text_processor.py
├── static/
│ ├── index.html
│ ├── style.css
│ └── script.js
└── requirements.txt

## License

MIT License
