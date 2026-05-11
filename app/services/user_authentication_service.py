"""
User Authentication Service
Phase 7: Multi-User Deployment - User Authentication and Authorization
JWT token-based authentication with user management
"""

import jwt
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class User:
    """User data model"""
    user_id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    role: str = "user"  # user, admin, researcher
    profile: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.profile is None:
            self.profile = {}

@dataclass
class AuthToken:
    """Authentication token data model"""
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime
    token_type: str = "access"

class UserAuthenticationService:
    """User authentication and authorization service"""
    
    def __init__(self, secret_key: str = None, users_file: str = None):
        self.project_root = Path("/home/jonat/ai-stack")
        self.users_file = users_file or self.project_root / "data" / "users.json"
        self.users_file.parent.mkdir(exist_ok=True)
        
        # JWT settings
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=7)
        
        # User storage
        self.users = {}
        self.active_tokens = {}
        
        # Load existing users
        self._load_users()
        
        # Create admin user if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self):
        """Load users from file"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                
                for user_id, user_data in users_data.items():
                    # Convert string dates back to datetime objects
                    created_at = datetime.fromisoformat(user_data["created_at"])
                    last_login = None
                    if user_data.get("last_login"):
                        last_login = datetime.fromisoformat(user_data["last_login"])
                    
                    user = User(
                        user_id=user_id,
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=user_data["password_hash"],
                        created_at=created_at,
                        last_login=last_login,
                        is_active=user_data.get("is_active", True),
                        role=user_data.get("role", "user"),
                        profile=user_data.get("profile", {})
                    )
                    
                    self.users[user_id] = user
                    
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def _save_users(self):
        """Save users to file"""
        try:
            users_data = {}
            
            for user_id, user in self.users.items():
                users_data[user_id] = {
                    "username": user.username,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "is_active": user.is_active,
                    "role": user.role,
                    "profile": user.profile
                }
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@faithh.local",
            password_hash=self._hash_password("admin123"),
            created_at=datetime.now(),
            role="admin",
            profile={"name": "System Administrator", "department": "System"}
        )
        
        self.users[admin_user.user_id] = admin_user
        self._save_users()
        print("🔑 Default admin user created (username: admin, password: admin123)")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _generate_token(self, user: User, token_type: str = "access") -> AuthToken:
        """Generate JWT token for user"""
        now = datetime.now()
        
        if token_type == "access":
            expires_at = now + self.token_expiry
        else:  # refresh token
            expires_at = now + self.refresh_token_expiry
        
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "token_type": token_type,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp())
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return AuthToken(
            token=token,
            user_id=user.user_id,
            expires_at=expires_at,
            created_at=now,
            token_type=token_type
        )
    
    def register_user(self, username: str, email: str, password: str, 
                     role: str = "user", profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Validate input
            if not username or not email or not password:
                return {"success": False, "error": "Username, email, and password are required"}
            
            # Check if username already exists
            for user in self.users.values():
                if user.username == username:
                    return {"success": False, "error": "Username already exists"}
                if user.email == email:
                    return {"success": False, "error": "Email already exists"}
            
            # Create new user
            user_id = f"user_{int(time.time() * 1000)}"
            
            new_user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=self._hash_password(password),
                created_at=datetime.now(),
                role=role,
                profile=profile or {}
            )
            
            self.users[user_id] = new_user
            self._save_users()
            
            # Generate tokens
            access_token = self._generate_token(new_user, "access")
            refresh_token = self._generate_token(new_user, "refresh")
            
            # Store active tokens
            self.active_tokens[access_token.token] = access_token
            self.active_tokens[refresh_token.token] = refresh_token
            
            return {
                "success": True,
                "user": {
                    "user_id": new_user.user_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role": new_user.role,
                    "created_at": new_user.created_at.isoformat(),
                    "profile": new_user.profile
                },
                "tokens": {
                    "access_token": access_token.token,
                    "refresh_token": refresh_token.token,
                    "expires_at": access_token.expires_at.isoformat()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with username and password"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username and u.is_active:
                    user = u
                    break
            
            if not user:
                return {"success": False, "error": "Invalid username or password"}
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                return {"success": False, "error": "Invalid username or password"}
            
            # Update last login
            user.last_login = datetime.now()
            self._save_users()
            
            # Generate tokens
            access_token = self._generate_token(user, "access")
            refresh_token = self._generate_token(user, "refresh")
            
            # Store active tokens
            self.active_tokens[access_token.token] = access_token
            self.active_tokens[refresh_token.token] = refresh_token
            
            return {
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "last_login": user.last_login.isoformat(),
                    "profile": user.profile
                },
                "tokens": {
                    "access_token": access_token.token,
                    "refresh_token": refresh_token.token,
                    "expires_at": access_token.expires_at.isoformat()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            # Check if token exists in active tokens
            if token not in self.active_tokens:
                return {"success": False, "error": "Token not found or expired"}
            
            token_data = self.active_tokens[token]
            
            # Check if token is expired
            if datetime.now() > token_data.expires_at:
                # Remove expired token
                del self.active_tokens[token]
                return {"success": False, "error": "Token expired"}
            
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Get user
            user = self.users.get(payload["user_id"])
            if not user or not user.is_active:
                return {"success": False, "error": "User not found or inactive"}
            
            return {
                "success": True,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "profile": user.profile
                },
                "token_type": payload["token_type"],
                "expires_at": token_data.expires_at.isoformat()
            }
            
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid token"}
        except Exception as e:
            return {"success": False, "error": f"Token verification failed: {str(e)}"}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            token_result = self.verify_token(refresh_token)
            
            if not token_result["success"]:
                return {"success": False, "error": "Invalid refresh token"}
            
            if token_result["token_type"] != "refresh":
                return {"success": False, "error": "Invalid token type"}
            
            # Get user
            user = self.users.get(token_result["user"]["user_id"])
            if not user or not user.is_active:
                return {"success": False, "error": "User not found or inactive"}
            
            # Generate new access token
            new_access_token = self._generate_token(user, "access")
            
            # Store new token
            self.active_tokens[new_access_token.token] = new_access_token
            
            return {
                "success": True,
                "access_token": new_access_token.token,
                "expires_at": new_access_token.expires_at.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": f"Token refresh failed: {str(e)}"}
    
    def logout_user(self, token: str) -> Dict[str, Any]:
        """Logout user by removing token"""
        try:
            if token in self.active_tokens:
                del self.active_tokens[token]
                return {"success": True, "message": "Logged out successfully"}
            else:
                return {"success": False, "error": "Token not found"}
        except Exception as e:
            return {"success": False, "error": f"Logout failed: {str(e)}"}
    
    def update_user_profile(self, user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.profile.update(profile)
            self._save_users()
            
            return {
                "success": True,
                "profile": user.profile
            }
            
        except Exception as e:
            return {"success": False, "error": f"Profile update failed: {str(e)}"}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                return {"success": False, "error": "Invalid old password"}
            
            # Update password
            user.password_hash = self._hash_password(new_password)
            self._save_users()
            
            # Remove all active tokens for user (force re-login)
            tokens_to_remove = []
            for token, token_data in self.active_tokens.items():
                if token_data.user_id == user_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.active_tokens[token]
            
            return {"success": True, "message": "Password changed successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Password change failed: {str(e)}"}
    
    def get_all_users(self, admin_user_id: str) -> Dict[str, Any]:
        """Get all users (admin only)"""
        try:
            # Verify requester is admin
            admin_user = self.users.get(admin_user_id)
            if not admin_user or admin_user.role != "admin":
                return {"success": False, "error": "Admin access required"}
            
            users_list = []
            for user in self.users.values():
                users_list.append({
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "is_active": user.is_active,
                    "profile": user.profile
                })
            
            return {
                "success": True,
                "users": users_list,
                "total_users": len(users_list)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get users: {str(e)}"}
    
    def deactivate_user(self, admin_user_id: str, target_user_id: str) -> Dict[str, Any]:
        """Deactivate user (admin only)"""
        try:
            # Verify requester is admin
            admin_user = self.users.get(admin_user_id)
            if not admin_user or admin_user.role != "admin":
                return {"success": False, "error": "Admin access required"}
            
            # Don't allow deactivating admin users
            target_user = self.users.get(target_user_id)
            if not target_user:
                return {"success": False, "error": "User not found"}
            
            if target_user.role == "admin":
                return {"success": False, "error": "Cannot deactivate admin users"}
            
            # Deactivate user
            target_user.is_active = False
            self._save_users()
            
            # Remove all active tokens for user
            tokens_to_remove = []
            for token, token_data in self.active_tokens.items():
                if token_data.user_id == target_user_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.active_tokens[token]
            
            return {"success": True, "message": "User deactivated successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"User deactivation failed: {str(e)}"}
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            total_users = len(self.users)
            active_users = len([u for u in self.users.values() if u.is_active])
            admin_users = len([u for u in self.users.values() if u.role == "admin"])
            researcher_users = len([u for u in self.users.values() if u.role == "researcher"])
            regular_users = len([u for u in self.users.values() if u.role == "user"])
            
            # Recent registrations (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_registrations = len([
                u for u in self.users.values() 
                if u.created_at > seven_days_ago
            ])
            
            # Active tokens
            active_tokens = len(self.active_tokens)
            
            return {
                "success": True,
                "statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "admin_users": admin_users,
                    "researcher_users": researcher_users,
                    "regular_users": regular_users,
                    "recent_registrations": recent_registrations,
                    "active_tokens": active_tokens
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get statistics: {str(e)}"}
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens"""
        try:
            now = datetime.now()
            expired_tokens = []
            
            for token, token_data in self.active_tokens.items():
                if now > token_data.expires_at:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.active_tokens[token]
            
            return len(expired_tokens)
            
        except Exception as e:
            print(f"Error cleaning up expired tokens: {e}")
            return 0

# Global instance
auth_service = UserAuthenticationService()