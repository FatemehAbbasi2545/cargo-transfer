"""Standalone client tests: no FastAPI, server imports, or running backend."""
from io import BytesIO
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from cargo_client.ui.api_client import APIClient


class APIClientTests(unittest.TestCase):
    def setUp(self):
        self.client = APIClient("http://localhost:8000/", timeout=3)

    def response(self, body):
        return BytesIO(json.dumps(body).encode())

    def login(self):
        with patch("cargo_client.ui.api_client.urlopen", return_value=self.response({
            "success": True, "user_id": 1, "user_name": "owner", "role": "cargo_owner",
        })):
            return self.client.login("owner", "Passw0rd*")

    def test_login_and_authenticated_request(self):
        result = self.login()
        self.assertEqual(result.data.user_id, 1)
        self.assertFalse(hasattr(result.data, "password"))
        with patch("cargo_client.ui.api_client.urlopen", return_value=self.response({
            "success": True, "data": [],
        })) as send:
            result = self.client.get_cargos_of_owner()
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:8000/cargos/mine")
        self.assertEqual(request.method, "GET")
        self.assertTrue(request.get_header("Authorization").startswith("Basic "))
        self.assertEqual(send.call_args.kwargs["timeout"], 3)

    def test_registration_sends_confirmation_without_credentials(self):
        self.login()
        with patch("cargo_client.ui.api_client.urlopen", return_value=self.response({
            "success": True, "user_id": 2,
        })) as send:
            result = self.client.register(name="Owner", user_name="owner", phone_number="09121112233",
                                          password="Passw0rd*", confirm_password="Passw0rd*", role="cargo_owner")
        self.assertTrue(result.success)
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:8000/auth/register")
        self.assertEqual(json.loads(request.data)["confirm_password"], "Passw0rd*")
        self.assertIsNone(request.get_header("Authorization"))

    def test_logout_prevents_authenticated_calls(self):
        self.login()
        self.client.logout()
        with patch("cargo_client.ui.api_client.urlopen") as send:
            self.assertFalse(self.client.get_all_cargos().success)
        send.assert_not_called()

    def test_failed_login_clears_previous_session(self):
        self.login()
        error = HTTPError("http://localhost", 401, "Unauthorized", {},
                          self.response({"detail": "Invalid password."}))
        with patch("cargo_client.ui.api_client.urlopen", side_effect=error):
            result = self.client.login("owner", "wrong")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Invalid password.")
        self.assertFalse(self.client.get_all_cargos().success)

    def test_validation_errors_are_readable(self):
        error = HTTPError("http://localhost", 422, "Invalid", {}, self.response({
            "detail": [{"loc": ["body", "new_password"], "msg": "Too short"}],
        }))
        with patch("cargo_client.ui.api_client.urlopen", side_effect=error):
            result = self.client.update_password(1, "short")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "body.new_password: Too short")

    def test_connection_failure_is_readable(self):
        with patch("cargo_client.ui.api_client.urlopen", side_effect=URLError("offline")):
            result = self.client.login("owner", "Passw0rd*")
        self.assertFalse(result.success)
        self.assertIn("Cannot connect", result.message)


if __name__ == "__main__":
    unittest.main()
