import os

from cargo_client.ui.api_client import APIClient
from cargo_client.ui.view_container import ViewContainer

if __name__ == "__main__":
    client = APIClient(os.environ.get("CARGO_API_URL", "http://127.0.0.1:8000"))
    try:
        app = ViewContainer(client)
        app.mainloop()
    finally:
        client.logout()
