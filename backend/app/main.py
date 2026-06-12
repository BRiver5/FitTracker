import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import Base, engine
from app.core.responses import ApiError, envelope
from app.routers import (
    analytics,
    auth,
    calorie_logs,
    exercises,
    sessions,
    users,
    weight_logs,
    workout_plans,
)
from app.seed import seed_exercises

logger = logging.getLogger("fittracker")

STATUS_MESSAGES = {
    400: "Bad request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not found",
    422: "Validation error",
    500: "Internal server error",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_exercises()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"^(exp|http)://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return envelope(None, exc.message, exc.status_code)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = str(exc.detail) if exc.detail else STATUS_MESSAGES.get(exc.status_code, "Error")
    return envelope(None, message, exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return envelope({"errors": errors}, "Validation error", 422)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return envelope(None, "Internal server error", 500)


@app.get("/health")
def health():
    return envelope({"status": "ok"})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workout_plans.router)
app.include_router(exercises.router)
app.include_router(sessions.router)
app.include_router(weight_logs.router)
app.include_router(calorie_logs.router)
app.include_router(analytics.router)
