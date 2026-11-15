# Cargo Transfer

Two independent applications communicate only over HTTP:

- `client/`: Tkinter desktop UI, HTTP client, local response models and UI events.
- `server/`: FastAPI endpoints, business services, repositories and SQLite.
- `tests/integration/`: tests that run the server in a separate process and call it from the client.

Each application directory can be copied and run independently. Python 3.12+ is
required; the client also needs Tkinter. See each application's README for details.

Start the server from the repository root:

```powershell
python -m pip install -r server/requirements.txt
python server/main.py
```

In another terminal, start the client:

```powershell
python client/main.py
```

Both default to `http://127.0.0.1:8000`. The client accepts `CARGO_API_URL`;
the server accepts `CARGO_API_HOST`, `CARGO_API_PORT`, and `CARGO_DB_PATH`.
The default database is `server/app.db`. To reuse an existing database,
set `CARGO_DB_PATH` to its absolute path before starting the server.

Server tests (from `server/`):

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Client tests (from `client/`, no server packages needed):

```powershell
python -m unittest discover -s tests -v
```

Integration tests (from the repository root, server dependencies required):

```powershell
python -m unittest discover -s tests/integration -v
```

Tests use temporary or in-memory databases and do not alter production data.
