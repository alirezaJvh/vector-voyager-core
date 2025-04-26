import faiss
from openai import OpenAI
from .config import OPENAI_API_KEY
import numpy as np



class VectorDBClient:
    def __init__(self, embedding_dim: int = 1536):
        if OPENAI_API_KEY == "":
            raise NotImplementedError("OpenAI API key is not set")
        self._client = None
        self._embedding_dim = embedding_dim
        self._openai_client = OpenAI()

    def init_client(self):
        if not self._client:
            self._client = faiss.IndexFlatIP(self._embedding_dim)
                
    def get_client(self):
        if not self._client:
            self.init_client()
        return self._client

    def get_embedding(self, text: str):
        response = self._openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = np.array(response.data[0].embedding).astype('float32')
        return embedding
        
    