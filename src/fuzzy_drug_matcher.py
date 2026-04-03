import difflib
from src.utils import setup_logger

logger = setup_logger(__name__)

class FuzzyDrugMatcher:
    """
    ML Pipeline Phase 3: Domain-Specific Fuzzy Matching.
    Corrects OCR errors by matching against a master drug database.
    """
    
    # This would ideally be a much larger list or a dynamic API call.
    # For now, we seed it with common drugs and any known OTC ones.
    DRUG_DATABASE = [
        "Paracetamol", "Acetaminophen", "Amoxicillin", "Azithromycin", 
        "Metformin", "Atorvastatin", "Amlodipine", "Omeprazole", 
        "Losartan", "Albuterol", "Gabapentin", "Lisinopril", 
        "Levothyroxine", "Sertraline", "Ibuprofen", "Aspirin", 
        "Cetirizine", "Loratadine", "Guaifenesin", "Dextromethorphan"
    ]

    @staticmethod
    def get_best_match(drug_name, threshold=0.7):
        """
        Matches a messy OCR name against the drug database.
        """
        if not drug_name or len(drug_name) < 3:
            return drug_name

        # 1. Direct match check
        if drug_name.capitalize() in [d.capitalize() for d in FuzzyDrugMatcher.DRUG_DATABASE]:
            return drug_name

        # 2. Fuzzy match
        matches = difflib.get_close_matches(drug_name.capitalize(), FuzzyDrugMatcher.DRUG_DATABASE, n=1, cutoff=threshold)
        
        if matches:
            logger.info(f"Fuzzy Match: '{drug_name}' corrected to '{matches[0]}'")
            return matches[0]
        
        # 3. If no match, try checking OpenFDA via service (Real-time correction)
        try:
            from src.drug_info_service import DrugInfoService
            fda_info = DrugInfoService.search_drug(drug_name)
            if fda_info:
                official_name = fda_info.get("brand_name") or fda_info.get("generic_name")
                if official_name:
                    logger.info(f"OpenFDA Match: '{drug_name}' corrected to '{official_name}'")
                    return official_name
        except Exception as e:
            logger.error(f"Fuzzy matching via OpenFDA failed: {e}")

        return drug_name # Return original if no high-confidence match
