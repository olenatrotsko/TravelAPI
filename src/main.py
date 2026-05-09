from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import create_tables
from core.exceptions import (
    NotFoundError, ConflictError, ValidationError,
    ExternalAPIError, UnauthorizedError,
)
from api.auth.router import router as auth_router
from api.users.router import router as users_router
from api.projects.router import router as projects_router
from api.places.router import router as places_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    description="Travel management API",
    lifespan=lifespan,
)

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.message})

@app.exception_handler(ExternalAPIError)
async def external_api_handler(request: Request, exc: ExternalAPIError):
    return JSONResponse(status_code=502, content={"detail": exc.message})

@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )

PREFIX = "/api/v1"
app.include_router(auth_router, prefix=PREFIX)
app.include_router(users_router, prefix=PREFIX)
app.include_router(projects_router, prefix=PREFIX)
app.include_router(places_router, prefix=PREFIX)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
