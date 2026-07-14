from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Resume(BaseModel):
    """
    Pydantic database representation of a Resume metadata record.
    """
    id: str = Field(..., alias="_id")
    user_id: str
    resume_name: str
    cloud_storage_url: str
    upload_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    candidate_name: str = "Unknown"
    skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
