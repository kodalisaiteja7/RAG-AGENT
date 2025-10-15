"""
User Management System
Handles user authentication, sessions, and user-specific knowledge bases
"""
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List


class UserManager:
    """Manages users, authentication, and user-specific data"""

    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users_dir = Path("user_data")
        self.users_dir.mkdir(exist_ok=True)
        self._load_users()

    def _load_users(self):
        """Load users from file"""
        if Path(self.users_file).exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            # Create default admin user
            self.users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "full_name": "Administrator"
                }
            }
            self._save_users()

    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user"""
        if username not in self.users:
            return False

        password_hash = self._hash_password(password)
        return self.users[username]["password_hash"] == password_hash

    def create_user(self, username: str, password: str, full_name: str, role: str = "user") -> bool:
        """Create a new user"""
        if username in self.users:
            return False

        self.users[username] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "full_name": full_name
        }

        # Create user-specific directory
        user_dir = self.users_dir / username
        user_dir.mkdir(exist_ok=True)

        # Initialize user KB with empty list
        user_kb_path = user_dir / "user_kb.json"
        with open(user_kb_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

        self._save_users()
        return True

    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username not in self.users or username == "admin":
            return False

        del self.users[username]
        self._save_users()
        return True

    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        if username not in self.users:
            return False

        self.users[username]["password_hash"] = self._hash_password(new_password)
        self._save_users()
        return True

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        if username not in self.users:
            return None

        user_data = self.users[username].copy()
        user_data.pop("password_hash", None)  # Don't expose password hash
        user_data["username"] = username
        return user_data

    def list_users(self) -> List[Dict]:
        """List all users (admin only)"""
        users_list = []
        for username, data in self.users.items():
            user_info = data.copy()
            user_info.pop("password_hash", None)
            user_info["username"] = username
            users_list.append(user_info)
        return users_list

    def is_admin(self, username: str) -> bool:
        """Check if user is admin"""
        return username in self.users and self.users[username].get("role") == "admin"

    def get_user_kb_path(self, username: str) -> str:
        """Get path to user's knowledge base"""
        return str(self.users_dir / username / "user_kb.json")

    def get_user_vector_db_path(self, username: str) -> str:
        """Get path to user's vector database"""
        return str(self.users_dir / username / "user_vectordb")


# Singleton instance
_user_manager = None

def get_user_manager() -> UserManager:
    """Get or create UserManager singleton"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
