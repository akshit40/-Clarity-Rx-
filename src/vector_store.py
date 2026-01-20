from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import Config
from src.utils import setup_logger
import time

logger = setup_logger(__name__)

class VectorStoreManager:
    """
    Manages interactions with Pinecone Vector DB.
    """
    def __init__(self):
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            self.pc.list_indexes()  # Test connection immediately
            logger.info("Pinecone connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone. Check your PINECONE_API_KEY. Error: {e}")
            self.pc = None

        self.index_name = Config.PINECONE_INDEX_NAME

        # Initialize Embeddings
        if Config.GOOGLE_API_KEY:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004",
                    google_api_key=Config.GOOGLE_API_KEY
                )
                logger.info("Google Embeddings initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Embeddings. Check your GOOGLE_API_KEY. Error: {e}")
                self.embeddings = None
        else:
            logger.warning("Google API Key missing for embeddings.")
            self.embeddings = None

        # Ensure index exists and connect
        if self.pc:
            self._ensure_index()
            try:
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to Pinecone index '{self.index_name}'.")
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone index '{self.index_name}': {e}")
                self.index = None
        else:
            self.index = None

    def _ensure_index(self):
        """Creates the index if it doesn't exist."""
        if not self.pc:
            logger.error("Pinecone not connected. Cannot ensure index.")
            return
        try:
            existing = self.pc.list_indexes().names()
            if self.index_name not in existing:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=Config.PINECONE_ENV
                    )
                )
                time.sleep(5)  # Wait for initialization
                logger.info(f"Pinecone index '{self.index_name}' created successfully.")
            else:
                logger.info(f"Pinecone index '{self.index_name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to create/check Pinecone index: {e}")

    def add_texts(self, texts, metadata_list, namespace=None):
        """
        Generic method to add texts to Pinecone.
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized. Cannot add texts.")
            return False
        if not self.index:
            logger.error("Pinecone index not available. Cannot add texts.")
            return False

        try:
            vectors = []
            for i, text in enumerate(texts):
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()
                vector_id = f"{namespace}_{text_hash}" if namespace else f"{text_hash}"

                embedding = self.embeddings.embed_query(text)

                meta = metadata_list[i].copy() if i < len(metadata_list) else {}
                meta["text"] = text

                vectors.append((vector_id, embedding, meta))

            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)

            logger.info(f"Stored {len(vectors)} texts in namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Failed to add texts to Pinecone: {e}")
            return False

    def add_prescription(self, prescription_id, text_chunks, metadata):
        """
        Embeds and stores prescription chunks.
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized. Cannot add prescription.")
            return False
        if not self.index:
            logger.error("Pinecone index not available. Cannot add prescription.")
            return False

        try:
            vectors = []
            for i, chunk in enumerate(text_chunks):
                vector_id = f"{prescription_id}_{i}"
                embedding = self.embeddings.embed_query(chunk)

                chunk_metadata = metadata.copy()
                chunk_metadata["text"] = chunk
                chunk_metadata["chunk_id"] = i
                chunk_metadata["prescription_id"] = prescription_id

                vectors.append((vector_id, embedding, chunk_metadata))

            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Stored {len(vectors)} chunks for prescription {prescription_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add prescription to Pinecone: {e}")
            return False

    def search(self, query, prescription_id=None, namespace=None, top_k=5):
        """
        Searches for relevant chunks.
        If prescription_id is provided, filters by that ID (Local Search).
        Otherwise, searches globally or in a specific namespace.
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized. Cannot search.")
            return []
        if not self.index:
            logger.error("Pinecone index not available. Cannot search.")
            return []

        try:
            query_embedding = self.embeddings.embed_query(query)

            filter_dict = {}
            if prescription_id:
                filter_dict = {"prescription_id": {"$eq": prescription_id}}

            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if prescription_id else None,
                namespace=namespace
            )

            return results.matches
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []