# Cargo Transfer Client

This directory is a standalone desktop application. It needs Python 3.12+ with
Tkinter and does not need server source code, FastAPI, or SQLite repositories.
HTTP and JSON access use the Python standard library.

From this directory:

```powershell
python main.py
```

The API defaults to `http://127.0.0.1:8000`. To connect to another server:

```powershell
$env:CARGO_API_URL = "https://your-server.example"
python main.py
```

The backend must be running. Cargo API calls use HTTP Basic credentials held in
memory after login and cleared on logout. Use HTTPS for a remote server.

Run standalone client tests:

```powershell
python -m unittest discover -s tests -v
```
