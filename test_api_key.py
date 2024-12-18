from dotenv import load_dotenv
import os

def test_api_key():
    # Force reload of environment variables
    load_dotenv(override=True)
    
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key loaded: {'YES' if api_key else 'NO'}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"First 5 chars of API key: {api_key[:5] if api_key else 'None'}")

if __name__ == "__main__":
    test_api_key() 