# Quick Start Guide

Get the AI Medical Diagnosis System running in 5 minutes!

## Prerequisites

- Python 3.9+
- 8GB+ RAM
- API keys for OpenAI or Anthropic (optional for testing)

## Installation

### 1. Run Setup Script

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create necessary directories
- Set up environment variables

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
nano .env
```

Add your keys:
```
OPENAI_API_KEY=sk-...
```

### 3. Process Sample Data

```bash
# Activate virtual environment
source venv/bin/activate

# Process sample data
python scripts/process_data.py
```

### 4. Start the Server

```bash
python scripts/run_server.py
```

The API will be available at: `http://localhost:8000`

## Quick Test

### Test via Web Interface

Open your browser: `http://localhost:8000/docs`

This opens the interactive API documentation where you can test endpoints.

### Test via cURL

```bash
# Health check
curl http://localhost:8000/health

# Get diagnosis (requires auth token)
curl -X POST "http://localhost:8000/api/v1/diagnosis" \
  -H "Authorization: Bearer demo_token" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST001",
    "age": 45,
    "gender": "male",
    "symptoms": ["headache", "fever"],
    "medical_history": [],
    "current_medications": [],
    "allergies": []
  }'
```

### Test via Python

```python
from src.agents.medical_diagnosis_agent import PatientData, MedicalDiagnosisAgent
import yaml

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create patient
patient = PatientData(
    patient_id="TEST001",
    age=45,
    gender="male",
    symptoms=["headache", "fever"],
    medical_history=[],
    current_medications=[],
    allergies=[]
)

# Initialize agent and get diagnosis
agent = MedicalDiagnosisAgent(config)
diagnosis = agent.diagnose(patient)
print(diagnosis)
```

## Next Steps

1. **Add Your Data**: Place medical datasets in `data/` directories
2. **Fine-tune Model**: Run `python scripts/fine_tune.py` (requires GPU)
3. **Index Knowledge**: Add medical literature to `data/medical_literature/`
4. **Configure**: Customize `config/config.yaml` for your needs

## Common Issues

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors
Make sure `.env` file exists and contains valid API keys.

### Port Already in Use
Change port in `.env`:
```
API_PORT=8001
```

## Documentation

- Full documentation: `README.md`
- Architecture: `docs/ARCHITECTURE.md`
- API docs: `docs/API_DOCUMENTATION.md`
- Interactive docs: `http://localhost:8000/docs`

## Support

For issues or questions, please refer to the main README.md or open an issue.
