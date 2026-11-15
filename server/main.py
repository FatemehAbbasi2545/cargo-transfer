"""Standalone API server entry point."""
import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.presentation.api.app:app",
        host=os.environ.get("CARGO_API_HOST", "127.0.0.1"),
        port=int(os.environ.get("CARGO_API_PORT", "8000")),
    )
