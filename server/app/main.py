from fastapi import FastAPI

from .database import init_db
from .controllers.root import router as root_router
from .controllers.user import router as user_router
from .controllers.task import router as task_router

def create_app() -> FastAPI:
    """Application factory to allow for easier testing."""
    app = FastAPI(title="Todo API", version="0.1.0")

    # Initialize database and create tables
    init_db()

    # Include API routers
    app.include_router(root_router)
    app.include_router(user_router)
    app.include_router(task_router)
    return app


app = create_app() 