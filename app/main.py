import os
import logging
import tensorflow as tf
import json

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error
tf.get_logger().setLevel('ERROR')  # Only show errors

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.services.resume_service import ResumeService
from app.utils.text_processor import TextProcessor
from app.utils.cleanup import cleanup_temp_dbs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Parser API")

# CORS and Static Files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize service
resume_service = ResumeService()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving index page: {str(e)}")
        raise HTTPException(status_code=500, detail="Error serving index page")

@app.post("/parse-resume/")
async def parse_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: str = Form(...)
):
    """Parse and analyze a resume file"""
    try:
        # Parse options
        selected_options = json.loads(options)
        
        # Validate file extension
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Process the resume with selected options
        result = await resume_service.process_resume(file, selected_options)
        
        # Schedule cleanup in background
        background_tasks.add_task(cleanup_temp_dbs)
        
        return result

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-parser")
async def test_parser():
    """Test endpoint for specific format"""
    processor = TextProcessor()
    processor.test_specific()
    return {"message": "Test complete, check logs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 