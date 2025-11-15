# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/` and `/health`) require Bearer token authentication.

```bash
Authorization: Bearer YOUR_TOKEN
```

## Endpoints

### Health Check

**GET** `/health`

Check system health and component status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "components": {
    "diagnosis_agent": true,
    "rag_system": true
  }
}
```

---

### Get Diagnosis

**POST** `/api/v1/diagnosis`

Generate AI-powered diagnosis and treatment recommendations.

**Request Body:**
```json
{
  "patient_id": "PT12345",
  "age": 45,
  "gender": "male",
  "symptoms": [
    "chest pain for 2 hours",
    "shortness of breath",
    "sweating"
  ],
  "medical_history": ["hypertension", "high cholesterol"],
  "current_medications": ["lisinopril", "atorvastatin"],
  "allergies": ["penicillin"],
  "vital_signs": {
    "blood_pressure": "150/95",
    "heart_rate": 98,
    "temperature": 37.2
  },
  "lab_results": {
    "troponin": "elevated"
  }
}
```

**Response:**
```json
{
  "diagnosis_id": "DX-20240115103000",
  "patient_id": "PT12345",
  "potential_diagnoses": [
    {
      "condition": "Acute Coronary Syndrome",
      "confidence": 0.85,
      "evidence": ["chest pain characteristics", "risk factors", "elevated troponin"]
    }
  ],
  "recommended_tests": [
    "ECG",
    "Cardiac enzyme panel",
    "Coronary angiography"
  ],
  "treatment_recommendations": [
    {
      "intervention": "Emergency cardiology consultation",
      "priority": "immediate",
      "evidence": "ACS guidelines 2023"
    }
  ],
  "confidence_score": 0.85,
  "supporting_evidence": ["Evidence-based references..."],
  "warnings": [
    "URGENT: Possible cardiac emergency - immediate evaluation required",
    "This AI-generated diagnosis must be reviewed by a licensed healthcare professional"
  ],
  "timestamp": "2024-01-15T10:30:00",
  "requires_review": true
}
```

---

### Real-time Consultation

**POST** `/api/v1/consultation`

Get AI consultation for specific medical questions.

**Request Body:**
```json
{
  "patient_request": {
    "patient_id": "PT12345",
    "age": 45,
    "gender": "male",
    "symptoms": ["headache"],
    "medical_history": ["migraine"],
    "current_medications": [],
    "allergies": []
  },
  "query": "What are the treatment options for migraine prevention?"
}
```

**Response:**
```json
{
  "patient_id": "PT12345",
  "query": "What are the treatment options for migraine prevention?",
  "response": "Based on current guidelines, migraine prevention options include...",
  "timestamp": "2024-01-15T10:30:00",
  "disclaimer": "This AI-generated response must be reviewed by a licensed healthcare professional"
}
```

---

### Search Medical Knowledge

**POST** `/api/v1/knowledge/search`

Search across medical literature, drug databases, and clinical trials.

**Request Body:**
```json
{
  "query": "hypertension treatment guidelines",
  "source_types": ["medical_literature", "treatment_guidelines"],
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "hypertension treatment guidelines",
  "results": [
    {
      "source": "medical_literature",
      "content": "ACC/AHA hypertension guidelines recommend...",
      "metadata": {
        "title": "2023 Hypertension Guidelines",
        "year": 2023
      },
      "score": 0.92
    }
  ],
  "total_results": 5,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Get Drug Information

**GET** `/api/v1/drug/{drug_name}`

Retrieve detailed drug information.

**Parameters:**
- `drug_name` (path): Name of the drug

**Example:** `GET /api/v1/drug/lisinopril`

**Response:**
```json
{
  "drug_name": "lisinopril",
  "information": [
    {
      "source": "drug_databases",
      "content": "Lisinopril is an ACE inhibitor used for hypertension...",
      "metadata": {
        "class": "ACE Inhibitor",
        "interactions": ["NSAIDs", "potassium supplements"]
      }
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Search Clinical Trials

**GET** `/api/v1/clinical-trials/{condition}`

Find relevant clinical trials for a condition.

**Parameters:**
- `condition` (path): Medical condition

**Example:** `GET /api/v1/clinical-trials/diabetes`

**Response:**
```json
{
  "condition": "diabetes",
  "trials": [
    {
      "source": "clinical_trials",
      "content": "Trial NCT12345: Novel GLP-1 agonist for type 2 diabetes...",
      "metadata": {
        "trial_id": "NCT12345",
        "phase": "Phase 3",
        "status": "Recruiting"
      },
      "score": 0.88
    }
  ],
  "total_trials": 10,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid patient data: age must be between 0 and 150"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing diagnosis: <error message>"
}
```

---

## Rate Limiting

Default rate limit: **100 requests per hour** per API key.

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705320600
```

---

## Example Usage

### Python Example

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your_auth_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get diagnosis
patient_data = {
    "patient_id": "PT001",
    "age": 45,
    "gender": "male",
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history": ["hypertension"],
    "current_medications": ["lisinopril"],
    "allergies": []
}

response = requests.post(
    f"{API_URL}/api/v1/diagnosis",
    headers=headers,
    json=patient_data
)

diagnosis = response.json()
print(diagnosis)
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/diagnosis" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT001",
    "age": 45,
    "gender": "male",
    "symptoms": ["chest pain"],
    "medical_history": ["hypertension"],
    "current_medications": ["lisinopril"],
    "allergies": []
  }'
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints.
