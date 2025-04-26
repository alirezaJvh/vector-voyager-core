import faiss
from openai import OpenAI
from .config import OPENAI_API_KEY
import numpy as np
import json
import asyncio
from .redis import RedisClient



class VectorDBClient:
    def __init__(self, embedding_dim: int = 1536, index_file: str = "faiss_index"):
        if OPENAI_API_KEY == "":
            raise NotImplementedError("OpenAI API key is not set")
        self._client = None
        self._embedding_dim = embedding_dim
        self._openai_client = OpenAI()
        self._redis_client = RedisClient()
        self._index_file = index_file
        self._init_index_counter()

    def _init_index_counter(self):
        # Initialize index counter and metadata prefix
        self._index_counter_key = f"{self._index_file}:counter"
        self._metadata_prefix = f"{self._index_file}:metadata:"

    def init_client(self):
        if not self._client:
            self._client = faiss.IndexFlatIP(self._embedding_dim)

    async def _get_redis(self):
        redis = await self._redis_client.get_client()
        return redis

    async def _get_next_index(self) -> int:
        """Get the next available index position"""
        redis = await self._get_redis()
        counter = await redis.incr(self._index_counter_key)
        # Return the previous value (0-indexed)
        return counter - 1

    async def _get_metadata(self, index_position: int) -> dict:
        redis = await self._get_redis()
        key = f"{self._metadata_prefix}{index_position}"

        metadata = await redis.hgetall(key)

        if not metadata:
            return None
        
        for k, v in metadata.items():
            try:
                metadata[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass

        return metadata

    async def _save_metadata(self, index_position: int, metadata: dict):
        redis = await self._redis_client.get_client()
        key = f"{self._metadata_prefix}{index_position}"

        string_metadata = {k: json.dumps(v) if not isinstance(v, str) else v
                            for k, v in metadata.items()}
        await redis.hset(key, mapping=string_metadata)
                
    def get_client(self):
        if not self._client:
            self.init_client()
        return self._client

    def get_embedding(self, text: str | list[str]) -> list[float]:
        response = self._openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embeddings = np.array([e.embedding for e in response.data]).astype('float32')
        if isinstance(text, list):
            embeddings = np.vstack(embeddings)
        return embeddings

    async def add_embedding(self, text: str, product_id: str) -> int:
        embedding = self.get_embedding(text)
        # Reshape for FAISS (expects 2D array)
        embedding_reshaped = embedding.reshape(1, -1)
        # add embedding
        index = self.get_client()
        index.add(embedding_reshaped)

        index_position = await self._get_next_index()
        # store metadata in redis
        await self._save_metadata(index_position, {
            "product_id": product_id,
            "review_text": text
        })

        return index_position

    async def add_embedding_batch(self, texts: list[str], product_ids: list[str]) -> list[int]:
        if len(texts) != len(product_ids):
            raise ValueError("texts and product_ids must have the same length")

        if not texts:
            return []
        # get embeddings and add them
        embeddings = self.get_embedding(texts)
        index = self.get_client()
        index.add(embeddings)

        # store metadata
        start_index = await self._get_next_index()
        index_positions = []

        for index, (text, product_id) in enumerate(zip(texts, product_ids)):
            index_position = start_index + index
            # TODO: make it better
            await self._save_metadata(index_position, {
                'product_id': product_id,
                'review_text': text
            })
            index_positions.append(index_position)

        redis = await self._get_redis()
        await redis.incrby(self._index_counter_key, len(texts))
        
        return index_positions

    async def search(self, text: str, top_k: int = 2):
        query_embedding = self.get_embedding(text)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')

        index = self.get_client()
        distances, indices = index.search(query_embedding, k=top_k)
        metadata = []
    
        for idx in indices[0]:
            if idx != -1:
                metadata.append(await self._get_metadata(idx))
   
        return distances, indices, metadata
    
    def total_embedding(self) -> int:
        index = self.get_client()
        return index.ntotal

    async def remove_all(self):
        index = self.get_client()
        index.reset()
        redis = await self._get_redis()
        
        # Delete all metadata keys
        keys, _ = await asyncio.gather(
            redis.keys(f"{self._metadata_prefix}*"),
            redis.delete(self._index_counter_key)
        )
        
        if keys:
            await redis.delete(*keys)
        # Reset index counter
        self._init_index_counter()
        
        

        

        
    