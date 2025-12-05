import google.generativeai as genai
from src.config import Config
from src.utils import setup_logger
import json
import os
import time

logger = setup_logger(__name__)

class PrescriptionExtractor:
    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            logger.warning("Google API Key not found")
            self.model = None
        else:
            try:
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)
                logger.info("PrescriptionExtractor initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None

    def extract_data(self, file_input):
        if not self.model:
            logger.error("Gemini model not initialized. Cannot extract data.")
            return None

        prompt = """
        You are an expert medical assistant. Analyze this prescription and extract the following information in JSON format.
        Focus strictly on the medicine details and instructions.
        
        {
            "date": "Date of prescription",
            "medicines": [
                {
                    "name": "Exact name of the tablet/medicine",
                    "quantity": "How much to take (e.g., 1 tablet, 5ml)",
                    "timing": {
                        "morning": "Yes/No",
                        "afternoon": "Yes/No",
                        "night": "Yes/No",
                        "instruction": "Before meal / After meal / Empty stomach / etc."
                    },
                    "frequency": "Raw frequency string (e.g., 1-0-1)",
                    "duration": "For how many days the medicine should be taken"
                }
            ],
            "notes": "Any special instructions"
        }
        If a field is missing, use "-". Return ONLY the JSON.
        """

        try:
            content = []
            content.append(prompt)
            
            if isinstance(file_input, str):
                if file_input.endswith(".pdf"):
                    sample_file = genai.upload_file(path=file_input, display_name="Prescription")
                    while sample_file.state.name == "PROCESSING":
                        time.sleep(2)
                        sample_file = genai.get_file(sample_file.name)
                    content.append(sample_file)
                else:
                    import PIL.Image
                    img = PIL.Image.open(file_input)
                    content.append(img)
            elif hasattr(file_input, 'read'):
                # Save temporarily and process
                pass
            else:
                # Assume PIL Image or list of images
                if isinstance(file_input, list):
                    content.extend(file_input)
                else:
                    content.append(file_input)

            response = self.model.generate_content(content)
            
            # Parse JSON from response
            text = response.text
            # Clean up markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())

        except Exception as e:
            import traceback
            logger.error(f"Extraction failed: {e}\n{traceback.format_exc()}")
            return None