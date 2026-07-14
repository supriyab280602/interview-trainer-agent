from pydantic import BaseModel, Field, field_validator
import re

class SignupRequest(BaseModel):
    """
    Request schema for user registration with robust validation rules.
    """
    full_name: str = Field(..., min_length=2, description="User's full name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    confirm_password: str = Field(..., min_length=6, description="Confirm password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class LoginRequest(BaseModel):
    """
    Request schema for user authentication.
    """
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower()
