from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.v1 import router as v1_router

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
    allow_origins=["*"],
    allow_headers=[
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "x-spoki-account",
        "x-spoki-user",
        "x-spoki-api-key",
        "x-spoki-platform-version",
        "x-secret",
    ],
)


@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}
