from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserProfile(BaseModel):
    """
    Sub-model for a user's career profile settings.
    """
    profile_name: str
    experience_level: str
    target_role: str
    resume_id: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class User(BaseModel):
    """
    Pydantic database representation of a User record.
    """
    id: str = Field(..., alias="_id")
    full_name: str
    email: str
    password_hash: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login: Optional[str] = None
    profile_picture_url: Optional[str] = None
    profiles: Dict[str, UserProfile] = Field(default_factory=dict)
    active_profile_name: Optional[str] = None
