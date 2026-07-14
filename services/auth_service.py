import logging
from typing import Dict, Any, Optional
from datetime import datetime
from services.cloudant_service import CloudantService
from schemas.auth import SignupRequest, LoginRequest
from models.user import User, UserProfile
from auth import hash_password, verify_password, generate_session_id

logger = logging.getLogger("AuthService")

class AuthService:
    """
    AuthService coordinates all session validation, registration, and user profiles.
    Backed by the Cloudant database service.
    """
    
    def __init__(self, db_service: CloudantService) -> None:
        self.db = db_service

    async def signup(self, req: SignupRequest) -> Optional[Dict[str, Any]]:
        """
        Register a new user in the Cloudant database.
        Checks for duplicate emails.
        """
        try:
            # Query if email exists
            query = {"selector": {"email": req.email}}
            existing_users = await self.db.query_documents("users", query)
            if existing_users:
                logger.warning(f"Registration failed: Email '{req.email}' already exists.")
                return None

            user_id = str(req.email) # Email is unique, use as identifier
            pw_hash = hash_password(req.password)
            
            user_data = User(
                _id=user_id,
                full_name=req.full_name,
                email=req.email,
                password_hash=pw_hash
            )
            
            success = await self.db.create_document("users", user_id, user_data.model_dump(by_alias=True))
            if success:
                logger.info(f"User registered successfully: {req.email}")
                return {"email": req.email, "full_name": req.full_name}
            return None
        except Exception as e:
            logger.error(f"Error during registration service execution: {str(e)}", exc_info=True)
            return None

    async def login(self, req: LoginRequest) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        Generates a new UUID session and registers it.
        """
        try:
            user_doc = await self.db.get_document("users", req.email)
            if not user_doc:
                logger.warning(f"Login failed: User '{req.email}' not found.")
                return None

            # Verify password hash
            if not verify_password(req.password, user_doc["password_hash"]):
                logger.warning(f"Login failed: Incorrect password for user '{req.email}'.")
                return None

            # Update last login timestamp in user doc
            user_doc["last_login"] = datetime.utcnow().isoformat()
            await self.db.update_document("users", req.email, user_doc)

            # Create session ID
            session_id = generate_session_id()
            session_doc = {
                "user_id": req.email,
                "created_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat()
            }
            
            # Save session to DB
            sess_success = await self.db.create_document("sessions", session_id, session_doc)
            if not sess_success:
                logger.error("Failed to store session in Cloudant database.")
                return None

            logger.info(f"User '{req.email}' successfully logged in. Session ID: {session_id}")
            return {
                "session_id": session_id,
                "email": user_doc["email"],
                "full_name": user_doc["full_name"],
                "active_profile": user_doc.get("active_profile_name"),
                "profiles": user_doc.get("profiles", {})
            }
        except Exception as e:
            logger.error(f"Error during login service execution: {str(e)}", exc_info=True)
            return None

    async def logout(self, session_id: str) -> bool:
        """
        Destroy an active session.
        """
        try:
            success = await self.db.delete_document("sessions", session_id)
            if success:
                logger.info(f"Session '{session_id}' deleted/destroyed.")
            return success
        except Exception as e:
            logger.error(f"Error during logout service execution: {str(e)}", exc_info=True)
            return False

    async def get_user_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user details using session ID.
        """
        try:
            session = await self.db.get_document("sessions", session_id)
            if not session:
                return None
                
            user_doc = await self.db.get_document("users", session["user_id"])
            if user_doc:
                # Update session activity
                session["last_active"] = datetime.utcnow().isoformat()
                await self.db.update_document("sessions", session_id, session)
            return user_doc
        except Exception as e:
            logger.error(f"Error getting user by session: {str(e)}", exc_info=True)
            return None

    async def create_or_update_profile(self, email: str, profile_name: str, exp_level: str, role: str) -> Optional[Dict[str, Any]]:
        """
        Create or update an career interview profile settings inside a user record.
        """
        try:
            user_doc = await self.db.get_document("users", email)
            if not user_doc:
                return None

            profiles = user_doc.get("profiles", {})
            
            # Keep resume_id if updating existing profile
            existing_resume = None
            if profile_name in profiles:
                existing_resume = profiles[profile_name].get("resume_id")

            new_profile = UserProfile(
                profile_name=profile_name,
                experience_level=exp_level,
                target_role=role,
                resume_id=existing_resume
            )

            profiles[profile_name] = new_profile.model_dump()
            user_doc["profiles"] = profiles
            user_doc["active_profile_name"] = profile_name
            user_doc["updated_at"] = datetime.utcnow().isoformat()

            success = await self.db.update_document("users", email, user_doc)
            if success:
                logger.info(f"Updated profile '{profile_name}' for user '{email}'.")
                return user_doc
            return None
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}", exc_info=True)
            return None

    async def set_active_profile(self, email: str, profile_name: str) -> bool:
        """
        Set active career profile for user session contexts.
        """
        try:
            user_doc = await self.db.get_document("users", email)
            if not user_doc or profile_name not in user_doc.get("profiles", {}):
                return False
                
            user_doc["active_profile_name"] = profile_name
            user_doc["updated_at"] = datetime.utcnow().isoformat()
            return await self.db.update_document("users", email, user_doc)
        except Exception as e:
            logger.error(f"Error setting active profile: {str(e)}")
            return False
