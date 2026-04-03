from pymongo import MongoClient
from datetime import datetime
import uuid
from src.config import Config
from src.utils import setup_logger

logger = setup_logger(__name__)

class MemoryManager:
    """
    Manages chat history and sessions - MongoDB.
    """
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=10000)
            self.client.admin.command('ping')  # Test connection
            self.db = self.client.get_database("prescription_db")
            self.sessions = self.db.sessions
            self.messages = self.db.messages
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"MemoryManager failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.sessions = None
            self.messages = None

    def get_or_create_session(self, user_id, prescription_id, title=None, filename=None, details=None, extracted_data=None):
        """
        Retrieves an existing session for the (user, prescription) pair,
        or creates a new one if it doesn't exist.
        """
        if self.sessions is None:
            logger.error("MongoDB not available.")
            return str(uuid.uuid4())

        try:
            existing_session = self.sessions.find_one({
                "user_id": user_id,
                "prescription_id": prescription_id
            })

            if existing_session:
                updates = {}
                if title and not existing_session.get("title"):
                    updates["title"] = title
                if filename and not existing_session.get("filename"):
                    updates["filename"] = filename
                if details and not existing_session.get("details"):
                    updates["details"] = details
                if extracted_data and not existing_session.get("extracted_data"):
                    updates["extracted_data"] = extracted_data

                if updates:
                    self.sessions.update_one(
                        {"_id": existing_session["_id"]},
                        {"$set": updates}
                    )
                return existing_session["session_id"]

            # Create new session
            session_id = str(uuid.uuid4())
            doc = {
                "session_id": session_id,
                "user_id": user_id,
                "prescription_id": prescription_id,
                "summary": "",
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            if title:
                doc["title"] = title
            if filename:
                doc["filename"] = filename
            if details:
                doc["details"] = details
            if extracted_data:
                doc["extracted_data"] = extracted_data

            self.sessions.insert_one(doc)
            logger.info(f"Created new session {session_id} for user {user_id} on prescription {prescription_id}")
            return session_id
        except Exception as e:
            logger.error(f"get_or_create_session failed: {e}")
            return str(uuid.uuid4())

    def get_session_info(self, session_id):
        """Retrieves full session info."""
        if self.sessions is None:
            return {}
        try:
            session = self.sessions.find_one({"session_id": session_id})
            return session if session else {}
        except Exception as e:
            logger.error(f"get_session_info failed: {e}")
            return {}

    def get_session_details(self, session_id):
        """Retrieves details (medicine summary) for a session."""
        if self.sessions is None:
            return ""
        try:
            session = self.sessions.find_one({"session_id": session_id})
            return session.get("details", "") if session else ""
        except Exception as e:
            logger.error(f"get_session_details failed: {e}")
            return ""

    def get_prescription_by_filename(self, user_id, filename):
        """Checks if a user has already uploaded a file with this name."""
        if self.sessions is None:
            return None
        try:
            session = self.sessions.find_one({
                "user_id": user_id,
                "filename": filename
            })
            if session:
                return session["prescription_id"]
            return None
        except Exception as e:
            logger.error(f"get_prescription_by_filename failed: {e}")
            return None

    def add_message(self, session_id, role, content):
        """Adds a message to the session history."""
        if self.messages is None:
            return
        try:
            self.messages.insert_one({
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            })
            self.update_last_active(session_id)
        except Exception as e:
            logger.error(f"add_message failed: {e}")

    def get_history(self, session_id, limit=10):
        """Retrieves recent messages for a session."""
        if self.messages is None:
            return []
        try:
            cursor = self.messages.find(
                {"session_id": session_id}
            ).sort("timestamp", 1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"get_history failed: {e}")
            return []

    def get_summary(self, session_id):
        """Retrieves the summary for a session."""
        if self.sessions is None:
            return ""
        try:
            session = self.sessions.find_one({"session_id": session_id})
            return session.get("summary", "") if session else ""
        except Exception as e:
            logger.error(f"get_summary failed: {e}")
            return ""

    def update_summary(self, session_id, new_summary):
        """Updates the session summary."""
        if self.sessions is None:
            return
        try:
            self.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"summary": new_summary, "last_active": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"update_summary failed: {e}")

    def update_last_active(self, session_id):
        """Updates the last active timestamp."""
        if self.sessions is None:
            return
        try:
            self.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"update_last_active failed: {e}")

    def get_user_prescriptions(self, user_id):
        """Returns list of dicts {id, title} that the user has interacted with."""
        if self.sessions is None:
            return []
        try:
            cursor = self.sessions.find(
                {"user_id": user_id, "prescription_id": {"$ne": "GLOBAL"}},
                {"prescription_id": 1, "title": 1, "last_active": 1}
            ).sort("last_active", -1)

            results = []
            seen_ids = set()
            for doc in cursor:
                p_id = doc["prescription_id"]
                if p_id not in seen_ids:
                    results.append({
                        "id": p_id,
                        "title": doc.get("title", f"Prescription {p_id[:8]}...")
                    })
                    seen_ids.add(p_id)
            return results
        except Exception as e:
            logger.error(f"get_user_prescriptions failed: {e}")
            return []

    def get_all_sessions(self):
        """Returns all sessions sorted by last active."""
        if self.sessions is None:
            return []
        try:
            return list(self.sessions.find().sort("last_active", -1))
        except Exception as e:
            logger.error(f"get_all_sessions failed: {e}")
            return []

    def save_otc_result(self, session_id, otc_result):
        """Saves the OTC analysis result to the session."""
        if self.sessions is None:
            return
        try:
            self.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"otc_result": otc_result}}
            )
        except Exception as e:
            logger.error(f"save_otc_result failed: {e}")

    def get_otc_result(self, session_id):
        """Retrieves the OTC analysis result for a session."""
        if self.sessions is None:
            return None
        try:
            session = self.sessions.find_one({"session_id": session_id})
            return session.get("otc_result") if session else None
        except Exception as e:
            logger.error(f"get_otc_result failed: {e}")
            return None