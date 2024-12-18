import os
import shutil
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def cleanup_temp_dbs(max_age_hours=24):
    """Clean up temporary Chroma DBs older than specified hours"""
    try:
        temp_dir = "temp_dbs"
        if not os.path.exists(temp_dir):
            return
            
        now = datetime.now()
        count = 0
        
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                created_time = datetime.fromtimestamp(os.path.getctime(item_path))
                age = now - created_time
                
                if age > timedelta(hours=max_age_hours):
                    shutil.rmtree(item_path)
                    count += 1
                    
        if count > 0:
            logger.info(f"Cleaned up {count} old temporary databases")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}") 