import os
from PIL import Image
import pypdf
from src.utils import setup_logger

logger = setup_logger(__name__)

class IngestionManager:
    """
    Handles loading and processing of input files (PDFs, Images).
    """
    
    @staticmethod
    def load_file(file_path):
        """
        Loads a file and returns its content suitable for Gemini.
        For images: returns PIL Image object.
        For PDFs: returns list of PIL Image objects (one per page) or text.
        
        For this specific use case with Gemini Vision, converting PDF pages to images 
        is often better for extraction if the PDF contains scanned data.
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png']:
            return [Image.open(file_path)]
        
        elif ext == '.pdf':
            # For simplicity in this version, we will extract text directly if possible,
            # but for a robust prescription extractor, converting to images is better.
            # Here we will try to extract text first.
            # If we want to use Gemini Vision on PDFs, we need to convert pages to images.
            # Let's assume we return the file path for the extractor to handle, 
            # or a list of images if we implement pdf2image.
            # Since we didn't add pdf2image to requirements, we will rely on Gemini's ability 
            # to process PDFs if uploaded via File API, or just extract text for now.
            # WAIT: The user wants "Input file = images and pdf".
            # Gemini 1.5/2.0 can handle PDFs directly via the File API.
            # So we might just return the path and let the extractor handle the upload.
            return file_path
            
        else:
            raise ValueError(f"Unsupported file type: {ext}")

