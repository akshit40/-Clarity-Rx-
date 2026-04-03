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
        ACT AS A PROFESSIONAL RADIOLOGIST AND PHARMACIST.
        You are looking at a medical document (handwritten note or prescription).
        
        CRITICAL GOALS:
        1. Extract Medicine Details if any are present.
        2. Extract Clinical Notes, Diagnosis, and Advice if no medicines are present.
        
        {
            "date": "Date of prescription",
            "medicines": [
                {
                    "name": "Corrected medicinal name",
                    "quantity": "Amount (e.g., 5ml, 1 tab)",
                    "timing": {
                        "morning": "1/0",
                        "afternoon": "1/0",
                        "night": "1/0",
                        "instruction": "Specific timing notes"
                    },
                    "frequency": "Raw pattern (e.g., OD, BD, TID)",
                    "duration": "Duration (e.g., 5 days)"
                }
            ],
            "clinical_summary": "Summary of observations, check-ups, and advice (e.g., 'Ultrasound required', 'No meds found')",
            "notes": "Any other instructions"
        }
        Return ONLY valid JSON.
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
                    # ML PIPELINE PHASE 1: Image Preprocessing
                    from src.image_processor import ImageProcessor
                    img = ImageProcessor.process_for_ocr(file_input)
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
            
            result_json = json.loads(text.strip())

            # ML PIPELINE PHASE 3: Domain-Specific Fuzzy Matching Correction
            from src.fuzzy_drug_matcher import FuzzyDrugMatcher
            for med in result_json.get("medicines", []):
                original_name = med.get("name", "")
                corrected_name = FuzzyDrugMatcher.get_best_match(original_name)
                med["name"] = corrected_name

            return result_json

        except Exception as e:
            import traceback
            logger.error(f"Extraction failed: {e}\n{traceback.format_exc()}")
            return None