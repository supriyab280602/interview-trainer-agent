from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

class ProfileCreateRequest(BaseModel):
    """
    Profile creation request fields.
    """
    profile_name: str = Field(..., min_length=2)
    experience_level: str = Field(..., description="Fresher, 1-3 Years, 3-5 Years, 5+ Years")
    target_role: str = Field(..., description="Target job title (e.g. Software Engineer)")

    @field_validator("experience_level")
    @classmethod
    def validate_experience(cls, v: str) -> str:
        valid = ["Fresher", "1-3 Years", "3-5 Years", "5+ Years", "1–3 Years", "3–5 Years"]
        cleaned = v.strip()
        # Normalise hyphen variants
        normalized = cleaned.replace("–", "-")
        if normalized not in [x.replace("–", "-") for x in valid]:
            raise ValueError(f"Experience level must be one of: {', '.join(valid)}")
        return normalized

class InterviewStartRequest(BaseModel):
    """
    Interview configuration request schema.
    """
    profile_name: str = Field(..., description="Name of the interview profile to base on")
    interview_type: str = Field(..., description="HR, Technical, Behavioral, Mixed")
    difficulty: str = Field(..., description="Easy, Medium, Hard, Adaptive")
    length: int = Field(5, description="Number of questions: 5, 10, 15")

    @field_validator("interview_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = ["HR", "Technical", "Behavioral", "Mixed"]
        if v not in valid:
            raise ValueError(f"Interview type must be one of: {', '.join(valid)}")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        valid = ["Easy", "Medium", "Hard", "Adaptive"]
        if v not in valid:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid)}")
        return v

    @field_validator("length")
    @classmethod
    def validate_length(cls, v: int) -> int:
        if v not in [5, 10, 15]:
            raise ValueError("Length must be 5, 10, or 15 questions")
        return v

class AnswerSubmitRequest(BaseModel):
    """
    Candidate answer submission schema.
    """
    interview_id: str = Field(..., description="Unique interview identifier")
    question_index: int = Field(..., description="Index of the question being answered (0-indexed)")
    answer: str = Field(..., min_length=2, description="Candidate's raw text response")
