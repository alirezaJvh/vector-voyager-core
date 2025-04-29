from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.v1 import router as v1_router
from src.common.config import get_settings

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

settings = get_settings()
allowed_origins = settings.ALLOWED_ORIGINS.split(",") if "," in settings.ALLOWED_ORIGINS else [settings.ALLOWED_ORIGINS]

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
    allow_origins=allowed_origins,
    allow_headers=["*"],
)


@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}
