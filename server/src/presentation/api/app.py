import os
from pathlib import Path

from fastapi import FastAPI

from src.infrastructure.data_access.sqlite_database import SQLiteDatabase
from src.infrastructure.data_access.sqlite_repository_factory import SQLiteRepositoryFactory
from src.application.services.business_services.user_business_service import UserBusinessService
from src.application.services.business_services.cargo_business_service import CargoBusinessService
from src.presentation.api.routes import auth, cargo

def create_app() -> FastAPI:
    app = FastAPI(title="Cargo Transfer API", version="1.0.0")

    # Composition root belongs only to the server application.
    default_db_path = Path(__file__).resolve().parents[3] / "app.db"
    db = SQLiteDatabase(os.environ.get("CARGO_DB_PATH", str(default_db_path)))
    repository_factory = SQLiteRepositoryFactory(db)

    auth.user_service = UserBusinessService(repository_factory.create_user_repository())
    cargo.cargo_service = CargoBusinessService(
        repository_factory.create_cargo_repository(),
        repository_factory.create_cargo_offer_repository(),
    )

    app.include_router(auth.router)
    app.include_router(cargo.router)

    @app.on_event("shutdown")
    def shutdown():
        db.close()

    return app

app = create_app()
