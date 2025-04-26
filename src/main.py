from fastapi import FastAPI
from api.v1 import router as v1_router
from db.vector_db import create_vector_db
from db.redis import RedisClient

vector_db = create_vector_db()
redis = RedisClient()

app = FastAPI()
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    redis_client = await redis.get_client()
    a = await redis_client.get("test")
    return {"Hello": "World", "b": a}


@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}