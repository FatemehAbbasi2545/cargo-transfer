# Cargo Transfer Server

This directory is a standalone FastAPI application. It needs Python 3.12+ and
does not import the desktop client or Tkinter.

From this directory:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The default address is `http://127.0.0.1:8000`; API documentation is at `/docs`.
You can also launch with Uvicorn directly:

```powershell
python -m uvicorn src.presentation.api.app:app --host 127.0.0.1 --port 8000
```

Configuration:

| Environment variable | Default |
| --- | --- |
| `CARGO_API_HOST` | `127.0.0.1` |
| `CARGO_API_PORT` | `8000` |
| `CARGO_DB_PATH` | `app.db` in this server directory |

If an existing `app.db` is stored elsewhere, set `CARGO_DB_PATH` to its absolute
path to retain existing accounts and cargo data.

Run server tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```
