"""Integration tests for cargo endpoints using an in-memory SQLite database."""
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.services.business_services.cargo_business_service import CargoBusinessService
from src.application.services.business_services.user_business_service import UserBusinessService
from src.common.entities.user import User
from src.common.exceptions import DatabaseError
from src.infrastructure.data_access.sqlite_database import SQLiteDatabase
from src.infrastructure.data_access.sqlite_repository_factory import SQLiteRepositoryFactory
from src.presentation.api.routes import auth, cargo

class CargoAPITests(unittest.TestCase):
    def setUp(self):
        SQLiteDatabase.reset_instance()
        self.db = SQLiteDatabase(":memory:")
        factory = SQLiteRepositoryFactory(self.db)
        self.previous_user_service = auth.user_service
        self.previous_cargo_service = cargo.cargo_service
        auth.user_service = UserBusinessService(factory.create_user_repository())
        cargo.cargo_service = CargoBusinessService(
            factory.create_cargo_repository(), factory.create_cargo_offer_repository(),
        )
        self.users = {}
        for index, (name, role) in enumerate([
            ("owner", "cargo_owner"), ("otherowner", "cargo_owner"),
            ("carrier", "cargo_carrier"), ("admin", "admin"),
        ]):
            user = User(name=name, user_name=name, password="Passw0rd*",
                        phone_number=f"0912111223{index}", role=role)
            self.assertTrue(auth.user_service.register(user).success)
            self.users[name] = user
        app = FastAPI()
        app.include_router(auth.router)
        app.include_router(cargo.router)
        self.client = TestClient(app)
        self.payload = {
            "title": "Furniture", "description": "Handle with care", "weight": 250,
            "origin": "Tehran", "destination": "Shiraz", "transport_type": "ground",
        }

    def tearDown(self):
        self.client.close()
        auth.user_service = self.previous_user_service
        cargo.cargo_service = self.previous_cargo_service
        SQLiteDatabase.reset_instance()

    def credentials(self, name):
        return (name, "Passw0rd*")

    def create_cargo(self, owner="owner", **changes):
        response = self.client.post("/cargos", json=self.payload | changes,
                                    auth=self.credentials(owner))
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["data"]["cargo_id"]

    def test_submit_cargo_request_and_transport_types(self):
        for transport_type in ["ground", "air", "sea"]:
            with self.subTest(transport_type=transport_type):
                cargo_id = self.create_cargo(transport_type=transport_type)
                saved = cargo.cargo_service.cargo_repository.get_by_id(cargo_id)
                self.assertEqual(saved.owner_id, self.users["owner"].user_id)
                self.assertEqual(saved.transport_type, transport_type)
                self.assertEqual(saved.title, self.payload["title"])

    def test_get_all_cargos_for_carrier_and_admin(self):
        ids = {self.create_cargo(), self.create_cargo("otherowner")}
        for name in ["carrier", "admin"]:
            response = self.client.get("/cargos", auth=self.credentials(name))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()["success"])
            self.assertEqual({item["cargo_id"] for item in response.json()["data"]}, ids)

    def test_get_cargos_of_owner_filters_other_owners(self):
        own_id = self.create_cargo()
        self.create_cargo("otherowner")
        response = self.client.get("/cargos/mine", auth=self.credentials("owner"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["cargo_id"] for item in response.json()["data"]], [own_id])

    def test_submit_price_offer_and_get_offers(self):
        cargo_id = self.create_cargo()
        other_id = self.create_cargo()
        path = f"/cargos/{cargo_id}/offers"
        response = self.client.post(path, json={"price": 1500, "message": "Available"},
                                    auth=self.credentials("carrier"))
        self.assertEqual(response.status_code, 201)
        offer = response.json()["data"]
        self.assertEqual(offer["cargo_id"], cargo_id)
        self.assertEqual(offer["carrier_id"], self.users["carrier"].user_id)
        self.assertEqual(offer["price"], 1500)
        self.assertEqual(offer["message"], "Available")
        self.assertGreater(offer["offer_id"], 0)
        self.client.post(f"/cargos/{other_id}/offers", json={"price": 2000},
                         auth=self.credentials("carrier"))
        for name in ["owner", "admin"]:
            result = self.client.get(path, auth=self.credentials(name))
            self.assertEqual(result.status_code, 200)
            self.assertEqual(len(result.json()["data"]), 1)
            self.assertEqual(result.json()["data"][0]["offer_id"], offer["offer_id"])

    def test_empty_lists(self):
        for path, name in [("/cargos", "carrier"), ("/cargos/mine", "owner")]:
            response = self.client.get(path, auth=self.credentials(name))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["data"], [])
        cargo_id = self.create_cargo()
        response = self.client.get(f"/cargos/{cargo_id}/offers", auth=self.credentials("owner"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [])

    def test_role_and_ownership_permissions(self):
        cargo_id = self.create_cargo()
        cases = [
            ("POST", "/cargos", "carrier", self.payload),
            ("POST", "/cargos", "admin", self.payload),
            ("GET", "/cargos", "owner", None),
            ("GET", "/cargos/mine", "carrier", None),
            ("GET", "/cargos/mine", "admin", None),
            ("POST", f"/cargos/{cargo_id}/offers", "owner", {"price": 100}),
            ("POST", f"/cargos/{cargo_id}/offers", "admin", {"price": 100}),
            ("GET", f"/cargos/{cargo_id}/offers", "otherowner", None),
            ("GET", f"/cargos/{cargo_id}/offers", "carrier", None),
        ]
        for method, path, name, payload in cases:
            with self.subTest(method=method, path=path, name=name):
                response = self.client.request(method, path, json=payload, auth=self.credentials(name))
                self.assertEqual(response.status_code, 403)

    def test_missing_or_invalid_credentials(self):
        for method, path, payload in [
            ("POST", "/cargos", self.payload), ("GET", "/cargos", None),
            ("GET", "/cargos/mine", None),
            ("POST", "/cargos/1/offers", {"price": 100}),
            ("GET", "/cargos/1/offers", None),
        ]:
            for credentials in [None, ("carrier", "wrong"), ("unknown", "Passw0rd*")]:
                with self.subTest(method=method, path=path, credentials=credentials):
                    response = self.client.request(method, path, json=payload, auth=credentials)
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(response.headers["www-authenticate"], "Basic")

    def test_unknown_cargo(self):
        for method, name, payload in [("POST", "carrier", {"price": 100}), ("GET", "owner", None)]:
            response = self.client.request(method, "/cargos/999/offers", json=payload,
                                           auth=self.credentials(name))
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json()["detail"], "Cargo not found.")

    def test_invalid_cargo_payloads(self):
        for changes in [{"weight": 0}, {"weight": -1}, {"title": ""},
                        {"origin": ""}, {"destination": ""}, {"transport_type": "invalid"}]:
            with self.subTest(changes=changes):
                response = self.client.post("/cargos", json=self.payload | changes,
                                            auth=self.credentials("owner"))
                self.assertEqual(response.status_code, 422)
        response = self.client.post("/cargos", json={}, auth=self.credentials("owner"))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(cargo.cargo_service.cargo_repository.get_all(), [])

    def test_invalid_offer_payloads_and_paths(self):
        cargo_id = self.create_cargo()
        for payload in [{}, {"price": 0}, {"price": -1}, {"price": "invalid"}]:
            response = self.client.post(f"/cargos/{cargo_id}/offers", json=payload,
                                        auth=self.credentials("carrier"))
            self.assertEqual(response.status_code, 422)
        for invalid_id in ["0", "-1", "abc"]:
            for method, name, payload in [("POST", "carrier", {"price": 100}), ("GET", "owner", None)]:
                response = self.client.request(method, f"/cargos/{invalid_id}/offers", json=payload,
                                               auth=self.credentials(name))
                self.assertEqual(response.status_code, 422)
        self.assertEqual(cargo.cargo_service.cargo_offer_repository.get_by_cargo(cargo_id), [])

    def test_database_failure_is_reported(self):
        with patch.object(cargo.cargo_service.cargo_repository, "get_all",
                          side_effect=DatabaseError("Database unavailable.")):
            response = self.client.get("/cargos", auth=self.credentials("carrier"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Database unavailable.")


if __name__ == "__main__":
    unittest.main()
