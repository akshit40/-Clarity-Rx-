import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.otc_manager import OTCManager
from src.config import Config

def test_otc_check():
    print(f"API Key loaded: {'Yes' if Config.GOOGLE_API_KEY else 'No'}")
    if not Config.GOOGLE_API_KEY:
        print("Attempting to reload .env...")
        from dotenv import load_dotenv
        load_dotenv()
        print(f"API Key loaded after reload: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")

    manager = OTCManager()
    
    # Sample medicines
    # "Crocin" should match "Paracetamol (Dolo 650, Crocin)"
    # "Amoxicillin" should NOT match (it's an antibiotic, not in list)
    medicines = ["Crocin", "Amoxicillin", "Gelusil", "UnknownMed"]
    
    print("Testing OTC Check with:", medicines)
    
    result = manager.check_medicines_with_llm(medicines)
    
    print("\nResult:")
    print(result)

if __name__ == "__main__":
    test_otc_check()
