# AI Travel Itinerary Generator - Application

FastAPI-based backend for the AI-Powered Travel Itinerary Generator.

## Structure

```
app/
├── src/
│   ├── main.py           # Main application entry point
│   ├── config.py         # Configuration management
│   ├── database.py       # Database models and connection
│   ├── rag/              # RAG implementation (TODO)
│   ├── llm/              # LLM integration (TODO)
│   └── utils/            # Utility functions (TODO)
├── models/               # ML models directory
├── tests/                # Test files (TODO)
├── Dockerfile            # Docker container definition
└── requirements.txt      # Python dependencies
```

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- OpenSearch

### Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Access the API:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## Docker

Build and run with Docker:

```bash
# Build
docker build -t travel-ai:latest .

# Run
docker run -p 8000:8000 \
  -e DATABASE_HOST=host.docker.internal \
  -e REDIS_ENDPOINT=host.docker.internal:6379 \
  -e OPENSEARCH_ENDPOINT=http://host.docker.internal:9200 \
  travel-ai:latest
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Generate Itinerary
```bash
POST /api/v1/itinerary/generate
Content-Type: application/json

{
  "destination": "Paris, France",
  "start_date": "2024-06-01",
  "end_date": "2024-06-07",
  "budget": 2000,
  "interests": ["art", "food", "history"],
  "group_size": 2
}
```

## Testing

```bash
pytest tests/
```

## Next Steps

1. Implement RAG functionality with OpenSearch
2. Integrate LLM for itinerary generation
3. Add user authentication
4. Implement caching with Redis
5. Add comprehensive tests
6. Set up CI/CD pipeline
