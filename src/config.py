import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file, overriding any existing system variables
load_dotenv(find_dotenv(), override=True)

class Config:
    """
    Configuration class to hold environment variables and settings.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    
    # Pinecone settings
    PINECONE_INDEX_NAME = "prescription-index"
    PINECONE_ENV = "us-east-1"

    # Gemini Model - Using a valid model based on available ListModels
    GEMINI_MODEL_NAME = "gemini-2.5-flash"

    # Paths
    DATA_DIR = os.path.join(os.getcwd(), "data")
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

    @staticmethod
    def validate():
        """Validate that all necessary API keys are present."""
        errors = []
        if not Config.MONGO_URI:
            errors.append("MONGO_URI is missing in .env")
        if not Config.PINECONE_API_KEY:
            errors.append("PINECONE_API_KEY is missing in .env")
        if not Config.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is missing in .env")
        if errors:
            for e in errors:
                print(f"[CONFIG ERROR] {e}")
            raise ValueError("One or more required environment variables are missing.")