from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="CareerOS API",
    version="0.1.0",
    description="CareerOS REST API",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.api_cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)