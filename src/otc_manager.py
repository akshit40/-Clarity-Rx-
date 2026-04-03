import json
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import Config
from src.utils import setup_logger
from src.otc_data import OTC_LIST_DATA

logger = setup_logger(__name__)

class OTCManager:
    OTC_LIST = OTC_LIST_DATA

    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL_NAME,
                google_api_key=Config.GOOGLE_API_KEY
            )
            logger.info("OTCManager LLM initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize OTCManager LLM: {e}")
            self.llm = None

        # Initialize Vector Store
        from src.vector_store import VectorStoreManager
        self.vector_store = VectorStoreManager()
        self.otc_namespace = "otc_medicines"
        self._initialize_otc_db()

    def _initialize_otc_db(self):
        """
        Ingests the OTC list into Pinecone only if not already present.
        Avoids re-embedding on every startup to save API calls.
        """
        try:
            logger.info("Initializing OTC Vector DB...")

            # Check if data already exists in Pinecone namespace
            if self.vector_store.index:
                try:
                    stats = self.vector_store.index.describe_index_stats()
                    ns_stats = stats.get("namespaces", {})
                    existing_count = ns_stats.get(self.otc_namespace, {}).get("vector_count", 0)

                    if existing_count >= len(self.OTC_LIST):
                        logger.info(f"OTC DB already has {existing_count} vectors. Skipping re-ingestion.")
                        return
                    else:
                        logger.info(f"OTC DB has {existing_count} vectors, expected {len(self.OTC_LIST)}. Re-ingesting...")
                except Exception as e:
                    logger.warning(f"Could not check Pinecone stats, proceeding with ingestion: {e}")

            # Extract texts and metadatas
            texts = [item['medicine_name'] for item in self.OTC_LIST]
            metadatas = []
            for item in self.OTC_LIST:
                meta = item.get('metadata', {}).copy()
                meta['source'] = 'general_otc_list'
                metadatas.append(meta)

            success = self.vector_store.add_texts(texts, metadatas, namespace=self.otc_namespace)
            if success:
                logger.info("OTC List ingested into Pinecone successfully.")
            else:
                logger.error("OTC List ingestion failed. Vector store may not be available.")

        except Exception as e:
            logger.error(f"Failed to initialize OTC DB: {e}")

    def search_otc_db(self, query, top_k=10):
        """
        Searches the OTC vector database for similar medicines.
        """
        try:
            matches = self.vector_store.search(query, namespace=self.otc_namespace, top_k=top_k)
            results = []
            for m in matches:
                results.append({
                    "Medicine Name": m.metadata['text'],
                    "Type": m.metadata.get('type', 'Unknown'),
                    "Score": round(m.score, 2)
                })
            return results
        except Exception as e:
            logger.error(f"OTC search failed: {e}")
            return []

    def get_otc_list(self):
        return self.OTC_LIST

    def check_medicines_with_llm(self, medicine_list):
        """
        Checks if the provided medicines are in the OTC list using Vector Search + LLM.
        """
        if not self.llm:
            logger.error("LLM not initialized. Cannot check medicines.")
            return {"otc_medicines": [], "consult_medicines": [], "error": "LLM not available"}

        logger.info("Checking medicines against OTC list using Vector Search + LLM")

        results = {"otc_medicines": [], "consult_medicines": []}

        for med in medicine_list:
            med_str = str(med)

            # Vector Search for candidates
            try:
                matches = self.vector_store.search(med_str, namespace=self.otc_namespace, top_k=3)
                candidates = [m.metadata['text'] for m in matches if m.score > 0.7]
            except Exception as e:
                logger.error(f"Vector search failed for {med_str}: {e}")
                candidates = []

            if not candidates:
                results["consult_medicines"].append({
                    "name": med_str.split('(')[0].strip(),
                    "reason": "No matching approved OTC medicine found in database."
                })
                continue

            # LLM Verification
            candidates_str = "\n".join(candidates)

            prompt = f"""
            You are a medical assistant. Verify if the extracted medicine is strictly equivalent to any of the allowed OTC candidates found.

            Extracted Medicine: "{med_str}"

            Allowed OTC Candidates (from database):
            {candidates_str}

            Instructions:
            1. Determine if the 'Extracted Medicine' matches any 'Allowed OTC Candidate' (Brand or Generic).
            2. Match must be safe and exact (e.g., "Crocin" matches "Paracetamol").
            3. Return JSON.

            Output Format:
            {{
                "is_otc": true/false,
                "matched_candidate": "Name of matched OTC item" or null,
                "reason": "Brief explanation"
            }}
            """

            try:
                # 1. Local Vector Search for candidates
                matches = self.vector_store.search(med_str, namespace=self.otc_namespace, top_k=3)
                candidates = [m.metadata['text'] for m in matches if m.score > 0.65]
                candidates_str = "\n".join(candidates) if candidates else "None"

                # 2. LLM Verification against local candidates
                response = self.llm.invoke(prompt.format(med_str=med_str, candidates_str=candidates_str))
                content = response.content.replace("```json", "").replace("```", "").strip()
                verification = json.loads(content)

                name_clean = med_str.split(':')[0].strip("- ").strip()

                if verification.get("is_otc"):
                    results["otc_medicines"].append({
                        "name": name_clean,
                        "reason": f"Matched with {verification.get('matched_candidate')}"
                    })
                else:
                    # 3. Fallback to OpenFDA (Government Database)
                    from src.drug_info_service import DrugInfoService
                    fda_info = DrugInfoService.search_drug(name_clean)
                    
                    if fda_info and fda_info.get("is_otc"):
                        results["otc_medicines"].append({
                            "name": name_clean,
                            "reason": f"Verified as OTC via OpenFDA ({fda_info.get('purpose', 'General Use')})"
                        })
                    else:
                        results["consult_medicines"].append({
                            "name": name_clean,
                            "reason": verification.get("reason", "Not a valid match with allowed list")
                        })

            except Exception as e:
                logger.error(f"Error checking medicine {med_str}: {e}")
                results["consult_medicines"].append({
                    "name": med_str,
                    "reason": "Error verifying safety"
                })

        return results