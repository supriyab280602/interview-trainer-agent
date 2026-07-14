import unittest
import asyncio
import os
import shutil
from auth import hash_password, verify_password, generate_session_id
from schemas.auth import SignupRequest, LoginRequest
from schemas.interview import ProfileCreateRequest, InterviewStartRequest
from services.cloudant_service import CloudantService
from services.auth_service import AuthService

class TestAuthSecurity(unittest.TestCase):
    """
    Validates password hashing and session generation utilities.
    """
    def test_password_hashing(self):
        password = "secure_password123"
        hashed = hash_password(password)
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_session_generation(self):
        sess_id1 = generate_session_id()
        sess_id2 = generate_session_id()
        self.assertNotEqual(sess_id1, sess_id2)
        self.assertEqual(len(sess_id1), 36) # UUID format length


class TestPydanticSchemas(unittest.TestCase):
    """
    Validates validation constraints on Pydantic schemas.
    """
    def test_signup_validation(self):
        # Valid Request
        req = SignupRequest(
            full_name="John Doe",
            email="john@doe.com",
            password="password123",
            confirm_password="password123"
        )
        self.assertEqual(req.full_name, "John Doe")

        # Invalid Email
        with self.assertRaises(ValueError):
            SignupRequest(
                full_name="John Doe",
                email="john_invalid_email",
                password="password123",
                confirm_password="password123"
            )

        # Password mismatch
        with self.assertRaises(ValueError):
            SignupRequest(
                full_name="John Doe",
                email="john@doe.com",
                password="password123",
                confirm_password="different_password"
            )

    def test_profile_creation_validation(self):
        # Valid Profile
        req = ProfileCreateRequest(
            profile_name="Dev Profile",
            experience_level="1-3 Years",
            target_role="AI Engineer"
        )
        self.assertEqual(req.experience_level, "1-3 Years")

        # Invalid experience level
        with self.assertRaises(ValueError):
            ProfileCreateRequest(
                profile_name="Dev Profile",
                experience_level="10 Years", # Invalid
                target_role="AI Engineer"
            )


class TestCloudantMockDatabase(unittest.IsolatedAsyncioTestCase):
    """
    Tests the CloudantService local mock database engine behavior.
    """
    async def asyncSetUp(self):
        # Ensure clean mock environment
        self.db = CloudantService()
        self.db.is_mock = True
        self.db.local_db_path = "test_db.json"
        self.db._init_local_db()
        self.auth = AuthService(self.db)

    async def asyncTearDown(self):
        if os.path.exists("test_db.json"):
            os.remove("test_db.json")

    async def test_document_crud(self):
        doc_id = "user_test_1"
        content = {"name": "Test Account", "active": True}
        
        # Create
        created = await self.db.create_document("users", doc_id, content)
        self.assertTrue(created)
        
        # Read
        fetched = await self.db.get_document("users", doc_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["name"], "Test Account")
        
        # Update
        content["name"] = "Updated Account"
        updated = await self.db.update_document("users", doc_id, content)
        self.assertTrue(updated)
        
        fetched_updated = await self.db.get_document("users", doc_id)
        self.assertEqual(fetched_updated["name"], "Updated Account")
        
        # Delete
        deleted = await self.db.delete_document("users", doc_id)
        self.assertTrue(deleted)
        
        fetched_deleted = await self.db.get_document("users", doc_id)
        self.assertIsNone(fetched_deleted)

    async def test_auth_signup_flow(self):
        signup_req = SignupRequest(
            full_name="Jane Doe",
            email="jane@doe.com",
            password="mysecurepass",
            confirm_password="mysecurepass"
        )
        
        user_res = await self.auth.signup(signup_req)
        self.assertIsNotNone(user_res)
        self.assertEqual(user_res["email"], "jane@doe.com")

        # Double signup check
        failed_signup = await self.auth.signup(signup_req)
        self.assertIsNone(failed_signup)


if __name__ == "__main__":
    unittest.main()
