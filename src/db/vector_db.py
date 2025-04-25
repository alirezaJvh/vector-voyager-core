import faiss
from openai import OpenAI
from .config import OPENAI_API_KEY
import numpy as np


if OPENAI_API_KEY == "":
    raise NotImplementedError("OpenAI API key is not set")

client = OpenAI()

def get_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = np.array(response.data[0].embedding).astype('float32')
    return embedding


def create_vector_db():
    embedding_dim = 1536
    index = faiss.IndexFlatIP(embedding_dim)
    return index