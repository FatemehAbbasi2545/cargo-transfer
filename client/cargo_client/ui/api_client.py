"""HTTP client shared by desktop frames."""
import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cargo_client.models import Response
from cargo_client.models import Cargo
from cargo_client.models import CargoOffer
from cargo_client.models import User
from cargo_client.enums import TransportType

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000", timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._credentials = None

    def logout(self):
        self._credentials = None

    def _request(self, method, path, payload=None, authenticated=False):
        headers = {"Accept": "application/json"}
        if authenticated:
            if self._credentials is None:
                return Response(False, "Please log in first.")
            username, password = self._credentials
            token = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
            headers["Authorization"] = f"Basic {token}"
        try:
            data = None
            if payload is not None:
                data = json.dumps(payload, allow_nan=False).encode()
                headers["Content-Type"] = "application/json"
            request = Request(self.base_url + path, data=data, headers=headers, method=method)
            with urlopen(request, timeout=self.timeout) as result:
                body = json.load(result)
            return Response(body.get("success", False), body.get("message", ""), body.get("data", body))
        except HTTPError as error:
            with error:
                try:
                    detail = json.load(error).get("detail", "API request failed.")
                    if isinstance(detail, list):
                        detail = "\n".join(
                            f"{'.'.join(str(part) for part in item.get('loc', []))}: {item.get('msg', 'Invalid input')}"
                            for item in detail
                        )
                    message = str(detail)
                except (ValueError, TypeError, AttributeError):
                    message = f"API request failed (HTTP {error.code})."
            return Response(False, message)
        except (URLError, TimeoutError, OSError):
            return Response(False, "Cannot connect to the API. Check that the server is running.")
        except (ValueError, TypeError, AttributeError):
            return Response(False, "Invalid request data or API response.")

    def login(self, user_name, password):
        self.logout()
        response = self._request("POST", "/auth/login", {"user_name": user_name, "password": password})
        if response.success:
            data = response.data
            response.data = User(user_id=data["user_id"], user_name=data["user_name"], role=data["role"])
            self._credentials = (user_name, password)
        return response

    def register(self, *, name, user_name, phone_number, password, confirm_password, role):
        return self._request("POST", "/auth/register", {
            "name": name, "user_name": user_name, "phone_number": phone_number,
            "password": password, "confirm_password": confirm_password, "role": role,
        })

    def update_password(self, user_id, new_password):
        response = self._request("PATCH", "/auth/update-password", {
            "user_id": user_id, "new_password": new_password,
        })
        if response.success:
            self.logout()
        return response

    def submit_cargo_request(self, title, description, weight, origin, destination, transport_type):
        response = self._request("POST", "/cargos", {
            "title": title, "description": description, "weight": weight,
            "origin": origin, "destination": destination,
            "transport_type": transport_type.value if isinstance(transport_type, TransportType) else transport_type,
        }, authenticated=True)
        if response.success:
            response.data = Cargo(**response.data)
        return response

    def _get_cargos(self, path):
        response = self._request("GET", path, authenticated=True)
        if response.success:
            response.data = [Cargo(**item) for item in response.data]
        return response

    def get_all_cargos(self):
        return self._get_cargos("/cargos")

    def get_cargos_of_owner(self):
        return self._get_cargos("/cargos/mine")

    def submit_price_offer(self, cargo_id, price, message=None):
        response = self._request("POST", f"/cargos/{cargo_id}/offers", {
            "price": price, "message": message,
        }, authenticated=True)
        if response.success:
            response.data = CargoOffer(**response.data)
        return response

    def get_offers_for_cargo(self, cargo_id):
        response = self._request("GET", f"/cargos/{cargo_id}/offers", authenticated=True)
        if response.success:
            response.data = [CargoOffer(**item) for item in response.data]
        return response
