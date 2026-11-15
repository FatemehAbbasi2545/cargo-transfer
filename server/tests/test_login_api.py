"""Login and registration API regression test, isolated from production data."""
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.application.services.business_services.user_business_service import UserBusinessService
from src.infrastructure.data_access.sqlite_database import SQLiteDatabase
from src.infrastructure.data_access.sqlite_repository_factory import SQLiteRepositoryFactory
from src.presentation.api.routes import auth


class LoginAPITests(unittest.TestCase):
    def setUp(self):
        SQLiteDatabase.reset_instance()
        db = SQLiteDatabase(":memory:")
        self.previous_service = auth.user_service
        auth.user_service = UserBusinessService(SQLiteRepositoryFactory(db).create_user_repository())
        app = FastAPI()
        app.include_router(auth.router)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        auth.user_service = self.previous_service
        SQLiteDatabase.reset_instance()

    def test_login_and_register(self):
        # 1) Register a fixture user through the service layer
        from src.presentation.api.routes import auth
        from src.common.entities.user import User
    
        auth.user_service.register(User(
            name="Test", user_name="apiuser",
            password="Passw0rd*", phone_number="09121112233",
            role="cargo_owner",
        ))
    
        # 2) Successful login
        r = self.client.post("/auth/login", json={"user_name": "apiuser", "password": "Passw0rd*"})
        print("valid login:", r.status_code, r.json())
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["role"] == "cargo_owner"
    
        # 3) Wrong password
        r = self.client.post("/auth/login", json={"user_name": "apiuser", "password": "wrong"})
        print("bad password:", r.status_code, r.json())
        assert r.status_code == 401
    
        # 4) Validation error (empty fields)
        r = self.client.post("/auth/login", json={"user_name": "", "password": ""})
        print("validation:", r.status_code)
        assert r.status_code == 422
    
        # 5) Successful registration
        r = self.client.post("/auth/register", json={
            "name": "API User", "user_name": "apireg",
            "phone_number": "09124445566", "password": "Passw0rd*",
            "confirm_password": "Passw0rd*", "role": "cargo_carrier",
        })
        print("register:", r.status_code, r.json())
        assert r.status_code == 201
        assert r.json()["success"] is True
        assert r.json()["user_id"] is not None
    
        # 6) Duplicate username -> 409
        r = self.client.post("/auth/register", json={
            "name": "API User", "user_name": "apireg",
            "phone_number": "09124445577", "password": "Passw0rd*",
            "confirm_password": "Passw0rd*", "role": "cargo_carrier",
        })
        print("duplicate:", r.status_code, r.json())
        assert r.status_code == 409
    
        # 7) Weak password -> 422 (schema) or 200/409 with message (service)
        r = self.client.post("/auth/register", json={
            "name": "X", "user_name": "weakpw",
            "phone_number": "09124445588", "password": "short",
            "confirm_password": "short", "role": "cargo_owner",
        })
        print("weak password:", r.status_code)
        assert r.status_code == 422
    
        # 8) Password mismatch -> 422
        r = self.client.post("/auth/register", json={
            "name": "X", "user_name": "mismatch",
            "phone_number": "09124445599", "password": "Passw0rd*",
            "confirm_password": "Other1*", "role": "cargo_owner",
        })
        print("mismatch:", r.status_code, r.json()["detail"][0]["msg"])
        assert r.status_code == 422
    
        # 9) Invalid role -> 422
        r = self.client.post("/auth/register", json={
            "name": "X", "user_name": "badrole",
            "phone_number": "09124444000", "password": "Passw0rd*",
            "confirm_password": "Passw0rd*", "role": "hacker",
        })
        print("bad role:", r.status_code)
        assert r.status_code == 422
    
        print("ALL API TESTS PASSED")


if __name__ == "__main__":
    unittest.main()
