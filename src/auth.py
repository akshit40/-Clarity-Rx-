import bcrypt
from pymongo import MongoClient
from datetime import datetime
from src.config import Config
from src.utils import setup_logger

logger = setup_logger(__name__)

class AuthManager:
    """
    Manages User Authentication (Login/Register).
    """
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=10000)
            self.client.admin.command('ping')  # Test connection
            self.db = self.client.get_database("prescription_db")
            self.users = self.db.users
            logger.info("AuthManager connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"AuthManager failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.users = None

    def register_user(self, username, password):
        """Registers a new user."""
        if self.users is None:
            return False, "Database not available. Please check your MONGO_URI."

        try:
            if self.users.find_one({"username": username}):
                return False, "Username already exists."

            if len(password) < 6:
                return False, "Password must be at least 6 characters."

            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            self.users.insert_one({
                "username": username,
                "password_hash": hashed,
                "created_at": datetime.utcnow()
            })
            logger.info(f"Registered user: {username}")
            return True, "User registered successfully."
        except Exception as e:
            logger.error(f"Registration failed for {username}: {e}")
            return False, f"Registration failed: {str(e)}"

    def login_user(self, username, password):
        """Authenticates a user."""
        if self.users is None:
            return False, "Database not available. Please check your MONGO_URI."

        try:
            user = self.users.find_one({"username": username})
            if not user:
                return False, "Invalid username or password."

            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                logger.info(f"User logged in: {username}")
                return True, "Login successful."
            else:
                return False, "Invalid username or password."
        except Exception as e:
            logger.error(f"Login failed for {username}: {e}")
            return False, f"Login failed: {str(e)}"