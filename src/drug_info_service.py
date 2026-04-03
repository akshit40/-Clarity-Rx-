import requests
import json
from src.utils import setup_logger

logger = setup_logger(__name__)

class DrugInfoService:
    BASE_URL = "https://api.fda.gov/drug/label.json"

    @staticmethod
    def search_drug(drug_name):
        """
        Search for a drug by name and return its purpose, dosage, and category.
        """
        params = {
            "search": f'openfda.brand_name:"{drug_name}" openfda.generic_name:"{drug_name}"',
            "limit": 1
        }
        
        try:
            logger.info(f"Searching OpenFDA for: {drug_name}")
            response = requests.get(DrugInfoService.BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("results"):
                    return None
                
                result = data["results"][0]
                
                # Extract key fields
                info = {
                    "brand_name": result.get("openfda", {}).get("brand_name", [drug_name])[0],
                    "generic_name": result.get("openfda", {}).get("generic_name", ["Unknown"])[0],
                    "purpose": result.get("purpose", ["Information not available"])[0],
                    "indications": result.get("indications_and_usage", ["Information not available"])[0],
                    "dosage": result.get("dosage_and_administration", ["Refer to doctor's instructions"])[0],
                    "is_otc": "OTC" in str(result.get("openfda", {}).get("product_type", [])),
                    "warnings": result.get("warnings", ["Information not available"])[0]
                }
                return info
            else:
                logger.warning(f"OpenFDA API returned status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error querying OpenFDA: {e}")
            return None

    @staticmethod
    def check_interaction(drug_a, drug_b):
        """
        Checks if two drugs have known interactions using OpenFDA labels.
        (Note: Professional check would use more specialized APIs, but label search is a good first-party approach).
        """
        # This is a basic implementation using label warning searches
        info_a = DrugInfoService.search_drug(drug_a)
        if not info_a: return None

        warnings = info_a.get("warnings", "").lower()
        if drug_b.lower() in warnings:
            return f"Known interaction: {drug_a} warnings mention {drug_b}."
        
        return None
