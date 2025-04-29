# AI-Enhanced Customer Feedback Explorer (Backend)

A FastAPI-based backend service that processes customer feedback data into vector embeddings and provides an API for natural language querying and LLM-powered insights.

## Overview

This backend is part of a full-stack application built to explore customer feedback insights intelligently. It enables users to upload Amazon review data (or any other product-review feedback data), vectorizes the feedback for similarity search, and supports natural language queries with LLM-generated insights.

The system leverages FAISS for in-memory vector search, Redis for metadata storage, OpenAI models for embedding and chat response.

## Tech Stack

- **Framework**: FastAPI
- **Python Version**: 3.12
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Metadata Storage**: Redis
- **Embeddings**: OpenAI Embeddings API (text-embedding-3-small)
- **LLM**: OpenAI Chat API
- **Deployment**: Docker, Gunicorn, Uvicorn

## API Endpoints

- `POST /api/v1/upload`: Upload CSV file containing customer feedback data
  - Accepts a CSV file with review text and product ID columns
  - Returns the total number of processed reviews and file size
- `POST /api/v1/retrieve-data`: Retrieve relevant feedback based on a natural language query
  - Accepts a query string and optional top_k parameter
  - Returns the most similar feedback items with similarity scores
- `POST /api/v1/llm`: Generate an LLM response based on retrieved feedback
  - Accepts a query string and optional top_k parameter
  - Returns an AI-generated response along with the source feedback items
- `GET /api/v1/total-embedding`: Get the total number of embeddings in the vector database
  - Returns the count of embeddings currently stored
- `GET /healthz`: Health check endpoint
  - Returns status "ok" if the service is running

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=redis_url
ALLOWED_ORIGINS=http://localhost:3000
APP_ENV=development
```

### Running with Docker

1. Build and start the containers:

   ```
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`

### Running Locally (Development)

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
src/
├── api/
│   └── v1/
│       ├── routing.py      # API endpoints
│       └── schemas.py      # Pydantic models
├── common/
│   └── config.py           # Configuration settings
├── db/
│   ├── redis.py            # Redis client
│   └── vector_db.py        # FAISS vector database
├── exceptions/
│   ├── enums.py            # Error enums
│   └── handler.py          # Exception handlers
├── services/
│   ├── chat_reply.py       # LLM integration
│   └── csv_uploader.py     # CSV processing
└── main.py                 # Application entry point
```

## Key Design Decisions and Assumptions

**Flexible CSV Upload:**

Users must specify which CSV columns represent the review text and the product ID. This design keeps the system general and avoids hardcoding assumptions about data format.

**Vector Storage Strategy:**
FAISS was chosen for in-memory similarity search as explicitly suggested in the assignment. However, FAISS doesn't natively support metadata storage, so Redis was added to handle feedback texts and associated fields separately.

**No LangChain for Assignment Scope:**
Although LangChain provides excellent abstractions and FAISS integration, I intentionally avoided using it to implement everything manually for better transparency and to match the assignment’s expectation of a "simple, lightweight" solution.

**In-Memory Storage Only for This Assignment:**
Since the project requirements emphasize an in-memory vector store, no persistent database was introduced at this stage.

**Batch Processing**:
Large CSV files are processed in batches to prevent memory issues.
This approach ensures scalability when dealing with large datasets

## Deployment (Railway)

This backend is deployed on Railway for easy cloud hosting.

- Railway provides a simple platform-as-a-service (PaaS) environment ideal for deploying small to medium-sized applications.

- Both the FastAPI backend and Redis service are deployed and managed via Railway's infrastructure.

- Environment variables (such as `OPENAI_API_KEY`, `REDIS_HOST`, `REDIS_PORT`) are configured directly in the Railway project settings.

- Continuous Deployment (CD) is set up by connecting the GitHub repository to Railway, ensuring that every push to the main branch automatically updates the live deployment.

## Future Improvements

1. **Scalability Enhancements**:

   - Integrate LangChain to handle retrieval, summarization, and LLM chaining more cleanly and efficiently.
   - Migrate from FAISS to Milvus or ChromaDB for production. These databases natively support vector search and metadata storage, improving scalability and durability.

2. **Performance Optimization**:

   - Implement caching for frequent queries
   - Optimize vector search parameters for better relevance
   - Add support for filtering by product ID or other metadata

3. **Security Enhancements**:

   - Implement rate limiting
   - Add authentication and authorization
   - Improve input validation and sanitization

4. **Monitoring and Logging**:
   - Add structured logging
   - Implement metrics collection
   - Set up alerting for critical errors
