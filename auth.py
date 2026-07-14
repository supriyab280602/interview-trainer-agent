import bcrypt
import uuid
import logging

logger = logging.getLogger("AuthUtils")

def hash_password(password: str) -> str:
    """
    Hash a clear-text password using bcrypt.
    
    Args:
        password (str): Plain text password.
        
    Returns:
        str: Decoded string representation of the password hash.
    """
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}", exc_info=True)
        raise RuntimeError("Password secure processing failed.") from e

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a clear-text password against a stored bcrypt hash.
    
    Args:
        password (str): Plain text password.
        hashed_password (str): Encoded password hash.
        
    Returns:
        bool: True if passwords match, False otherwise.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}", exc_info=True)
        return False

def generate_session_id() -> str:
    """
    Generate a secure random session ID using UUID4.
    
    Returns:
        str: Unique session identifier.
    """
    return str(uuid.uuid4())
