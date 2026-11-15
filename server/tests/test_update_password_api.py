"""Password update API tests using an isolated in-memory database."""
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.services.business_services.user_business_service import UserBusinessService
from src.infrastructure.data_access.sqlite_database import SQLiteDatabase
from src.infrastructure.data_access.sqlite_user_repository import SQLiteUserRepository
from src.presentation.api.routes import auth

class UpdatePasswordAPITests(unittest.TestCase):
    def setUp(self):
        SQLiteDatabase.reset_instance()
        self.db = SQLiteDatabase(":memory:")
        self.previous_service = auth.user_service
        auth.user_service = UserBusinessService(SQLiteUserRepository(self.db, self.db))
        app = FastAPI()
        app.include_router(auth.router)
        self.client = TestClient(app)
        response = self.client.post("/auth/register", json={
            "name": "Test User", "user_name": "passwordtest",
            "phone_number": "09121112233", "password": "Passw0rd*",
            "confirm_password": "Passw0rd*",
        })
        self.assertEqual(response.status_code, 201)
        self.user_id = response.json()["user_id"]

    def tearDown(self):
        self.client.close()
        auth.user_service = self.previous_service
        SQLiteDatabase.reset_instance()

    def test_updated_password_can_be_used_to_login(self):
        response = self.client.patch("/auth/update-password", json={
            "user_id": self.user_id, "new_password": "NewPass1@",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "message": "Operation successful"})
        for password, expected_status in [("Passw0rd*", 401), ("NewPass1@", 200)]:
            login = self.client.post("/auth/login", json={
                "user_name": "passwordtest", "password": password,
            })
            self.assertEqual(login.status_code, expected_status)

    def test_weak_password_is_rejected_without_changing_password(self):
        response = self.client.patch("/auth/update-password", json={
            "user_id": self.user_id, "new_password": "abcdefgh",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("The password must", response.json()["detail"])
        login = self.client.post("/auth/login", json={
            "user_name": "passwordtest", "password": "Passw0rd*",
        })
        self.assertEqual(login.status_code, 200)

    def test_unknown_user_is_rejected(self):
        response = self.client.patch("/auth/update-password", json={
            "user_id": self.user_id + 1, "new_password": "NewPass1@",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "No user found with this ID.")

    def test_invalid_request_is_rejected(self):
        for payload in [
            {},
            {"user_id": 0, "new_password": "NewPass1@"},
            {"user_id": self.user_id, "new_password": "short"},
        ]:
            with self.subTest(payload=payload):
                response = self.client.patch("/auth/update-password", json=payload)
                self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
