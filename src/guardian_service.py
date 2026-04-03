import google.generativeai as genai
from src.config import Config
from src.utils import setup_logger
import json

logger = setup_logger(__name__)

class GuardianService:
    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            logger.warning("Google API Key not found for GuardianService")
            self.model = None
        else:
            try:
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model in Guardian: {e}")
                self.model = None

    def analyze(self, prescription_details: str):
        """
        Takes the extracted prescription details and returns advanced safety and savings insights.
        """
        if not self.model:
            return {"error": "AI not initialized."}

        prompt = f"""
        ACT AS A WORLD-CLASS CLINICAL PHARMACIST AND MEDICAL SAFETY AI.
        Analyze the following prescription details and provide a comprehensive safety and savings report in strict JSON format.

        PRESCRIPTION DETAILS:
        {prescription_details}

        CRITICAL TASKS:
        1. DDI (Drug-Drug Interactions): Check if any of these medicines interact dangerously with each other. If there's only 1 medicine, report "None".
        2. Food-Drug Safety: What foods/drinks must the patient explicitly avoid while taking these?
        3. Side-Effects: List the top 2 common side effects to watch out for.
        4. Lifestyle Recovery: Provide 2 non-medical, natural lifestyle tips for the likely condition treated by these meds.
        5. Generic Savings: For every branded medicine, name its cheaper generic counterpart.

        EXPECTED JSON FORMAT:
        {{
            "ddi_alert": "Red Alert/Warning text OR 'No known dangerous interactions.'",
            "food_warnings": ["Warning 1", "Warning 2"],
            "side_effects": ["Side effect 1", "Side effect 2"],
            "lifestyle_tips": ["Tip 1", "Tip 2"],
            "generics": [
                {{"brand": "Branded Name", "generic": "Cheaper Generic Alternative"}}
            ]
        }}
        Return ONLY valid JSON. Keep advice concise.
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())
        except Exception as e:
            logger.error(f"Guardian Analysis failed: {e}")
            return {"error": str(e)}

guardian_service = GuardianService()
