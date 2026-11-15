"""End-to-end tests: standalone client talks to a separate server process."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "client"))
from cargo_client.enums import TransportType
from cargo_client.ui.api_client import APIClient


class UIAPIClientTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        environment = os.environ.copy()
        environment.update(CARGO_API_HOST="127.0.0.1", CARGO_API_PORT=str(port),
                           CARGO_DB_PATH=str(Path(temporary.name) / "test.db"))
        self.log_path = Path(temporary.name) / "server.log"
        self.log = self.log_path.open("w", encoding="utf-8")
        self.addCleanup(self.log.close)
        self.process = subprocess.Popen(
            [sys.executable, "main.py"], cwd=ROOT / "server", env=environment,
            stdout=self.log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.addCleanup(self.stop_server)
        base_url = f"http://127.0.0.1:{port}"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and self.process.poll() is None:
            try:
                with urlopen(base_url + "/openapi.json", timeout=0.2) as result:
                    self.assertEqual(result.status, 200)
                break
            except (URLError, OSError):
                time.sleep(0.05)
        else:
            self.fail("Server failed to start: " + self.log_path.read_text(encoding="utf-8"))
        self.client = APIClient(base_url, timeout=2)

    def stop_server(self):
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)

    def register(self, name, role, phone):
        result = self.client.register(name=name, user_name=name, phone_number=phone,
                                      password="Passw0rd*", confirm_password="Passw0rd*", role=role)
        self.assertTrue(result.success, result.message)
        return result.data["user_id"]

    def test_full_owner_and_carrier_flow_over_http(self):
        owner_id = self.register("owner", "cargo_owner", "09121112233")
        carrier_id = self.register("carrier", "cargo_carrier", "09121112234")
        result = self.client.login("owner", "Passw0rd*")
        self.assertTrue(result.success)
        self.assertEqual(result.data.user_id, owner_id)
        self.assertFalse(hasattr(result.data, "password"))
        self.assertEqual(self.client.get_cargos_of_owner().data, [])
        result = self.client.submit_cargo_request("Furniture", "Careful", 10, "Tehran", "Shiraz", TransportType.GROUND)
        self.assertTrue(result.success, result.message)
        cargo_id = result.data.cargo_id
        self.assertEqual(result.data.owner_id, owner_id)
        self.assertEqual(self.client.get_cargos_of_owner().data[0].cargo_id, cargo_id)
        self.assertEqual(self.client.get_offers_for_cargo(cargo_id).data, [])
        self.client.logout()
        self.assertFalse(self.client.get_all_cargos().success)
        self.assertTrue(self.client.login("carrier", "Passw0rd*").success)
        self.assertEqual(self.client.get_all_cargos().data[0].cargo_id, cargo_id)
        result = self.client.submit_price_offer(cargo_id, 100, "Ready")
        self.assertTrue(result.success, result.message)
        self.assertEqual(result.data.carrier_id, carrier_id)
        self.assertTrue(self.client.login("owner", "Passw0rd*").success)
        offer = self.client.get_offers_for_cargo(cargo_id).data[0]
        self.assertEqual(offer.price, 100)
        self.assertEqual(offer.message, "Ready")
        self.assertTrue(self.client.update_password(owner_id, "NewPass1@").success)
        self.assertFalse(self.client.get_cargos_of_owner().success)
        self.assertFalse(self.client.login("owner", "Passw0rd*").success)
        self.assertTrue(self.client.login("owner", "NewPass1@").success)

    def test_validation_permission_and_not_found_errors(self):
        self.register("owner", "cargo_owner", "09121112233")
        self.client.login("owner", "Passw0rd*")
        result = self.client.get_all_cargos()
        self.assertFalse(result.success)
        self.assertIn("admin or a cargo carrier", result.message)
        result = self.client.submit_cargo_request("Furniture", "", -1, "Tehran", "Shiraz", "ground")
        self.assertFalse(result.success)
        self.assertIn("weight", result.message)
        result = self.client.get_offers_for_cargo(999)
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Cargo not found.")
        self.assertFalse(self.client.login("owner", "wrong").success)
        self.assertFalse(self.client.get_cargos_of_owner().success)

    def test_network_errors_are_returned_to_ui(self):
        with patch("cargo_client.ui.api_client.urlopen", side_effect=URLError("offline")):
            result = self.client.login("owner", "Passw0rd*")
        self.assertFalse(result.success)
        self.assertIn("Cannot connect", result.message)


if __name__ == "__main__":
    unittest.main()
