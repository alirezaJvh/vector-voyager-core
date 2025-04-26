from fastapi import FastAPI
from api.v1 import router as v1_router
from db.vector_db import VectorDBClient
from db.redis import RedisClient

vector_db = VectorDBClient()
redis = RedisClient()

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}