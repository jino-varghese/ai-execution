# AI-Powered Medical Diagnosis and Treatment Recommendations System

A comprehensive AI system that assists healthcare professionals with diagnosis and treatment recommendations using Large Language Models (LLMs), Retrieval Augmented Generation (RAG), and fine-tuning on medical datasets.

## 🏥 Overview

This system provides healthcare professionals with:
- AI-powered diagnosis suggestions based on patient symptoms and medical history
- Treatment recommendations backed by medical literature
- Real-time consultation assistance
- Access to latest research papers, drug databases, and clinical trials
- Safety checks and drug interaction warnings

## ⚠️ Important Disclaimer

**This system is designed to ASSIST healthcare professionals, not replace them.**

- All AI-generated recommendations must be reviewed by licensed medical personnel
- This system is for educational and research purposes
- Not approved for clinical use without proper validation and regulatory approval
- Always follow local medical regulations and guidelines

## 🚀 Key Features

### 1. LLM Fine-Tuning
- Fine-tune large language models on medical literature, patient records, and treatment protocols
- Support for parameter-efficient fine-tuning using LoRA (Low-Rank Adaptation)
- Compatible with popular open-source models (LLaMA, etc.)

### 2. RAG for Knowledge Retrieval
- Vector database integration for fast semantic search
- Retrieves information from:
  - Medical literature and research papers
  - Drug interaction databases
  - Clinical trial data
  - Treatment guidelines and protocols
- Real-time access to latest medical knowledge

### 3. Medical Diagnosis Agent
- Multi-step reasoning for complex medical cases
- Differential diagnosis generation
- Evidence-based recommendations with citations
- Safety validation and red flag detection
- Drug interaction checking

### 4. Healthcare Professional Interface
- RESTful API for easy integration
- Secure authentication
- HIPAA-compliant data handling
- Real-time consultation endpoints

## 📁 Project Structure

```
ai-execution/
├── config/
│   └── config.yaml              # System configuration
├── src/
│   ├── agents/
│   │   └── medical_diagnosis_agent.py  # Main diagnosis agent
│   ├── rag/
│   │   └── medical_rag.py       # RAG system for knowledge retrieval
│   ├── preprocessing/
│   │   └── data_processor.py    # Data preprocessing pipeline
│   ├── models/
│   │   └── fine_tuning.py       # LLM fine-tuning module
│   ├── api/
│   │   └── main.py              # FastAPI application
│   └── utils/
│       ├── safety_checks.py     # Safety validation
│       └── medical_terminology.py  # Medical NLP processing
├── data/
│   ├── raw/                     # Raw medical datasets
│   ├── processed/               # Processed training data
│   ├── medical_literature/      # Medical papers and literature
│   ├── clinical_trials/         # Clinical trial data
│   └── sample_data/             # Sample data for testing
├── tests/                       # Unit and integration tests
├── docs/                        # Documentation
└── requirements.txt             # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- CUDA-capable GPU (recommended for fine-tuning)
- 16GB+ RAM recommended

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-execution
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download required models**
```bash
# Download spaCy medical models
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz
```

5. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
```

6. **Initialize the database**
```bash
python scripts/initialize_db.py
```

## 📚 Usage

### 1. Data Preprocessing

Process medical datasets for fine-tuning:

```python
from src.preprocessing.data_processor import MedicalDataProcessor

processor = MedicalDataProcessor(config)

# Process patient records
processor.process_patient_records(
    input_file="data/raw/patient_records.csv",
    output_file="data/processed/patient_records.jsonl"
)

# Process medical literature
processor.process_medical_literature(
    input_directory="data/medical_literature",
    output_file="data/processed/medical_literature.jsonl"
)

# Create fine-tuning dataset
processor.create_fine_tuning_dataset()
```

### 2. Fine-Tuning the LLM

```python
from src.models.fine_tuning import MedicalLLMFineTuner

fine_tuner = MedicalLLMFineTuner(config)

# Load base model
fine_tuner.load_base_model("meta-llama/Llama-2-70b-hf")

# Prepare for efficient fine-tuning
fine_tuner.prepare_peft_model()

# Fine-tune on medical data
fine_tuner.fine_tune(
    train_dataset_path="data/processed/fine_tuning_dataset.jsonl",
    output_dir="models/fine_tuned"
)
```

### 3. Index Medical Knowledge

```python
from src.rag.medical_rag import MedicalRAG

rag = MedicalRAG(config['rag'])

# Index medical literature
rag.index_documents(
    source_name="medical_literature",
    documents_path="data/medical_literature"
)

# Index drug database
rag.index_documents(
    source_name="drug_databases",
    documents_path="data/drug_databases"
)
```

### 4. Running the API Server

```bash
# Start the API server
python src/api/main.py

# Or using uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 5. Using the Diagnosis Agent

**Via Python:**

```python
from src.agents.medical_diagnosis_agent import MedicalDiagnosisAgent, PatientData

agent = MedicalDiagnosisAgent(config)

patient = PatientData(
    patient_id="PT001",
    age=45,
    gender="male",
    symptoms=["chest pain", "shortness of breath"],
    medical_history=["hypertension"],
    current_medications=["lisinopril"],
    allergies=["penicillin"]
)

diagnosis = agent.diagnose(patient)
print(diagnosis)
```

**Via API:**

```bash
curl -X POST "http://localhost:8000/api/v1/diagnosis" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PT001",
    "age": 45,
    "gender": "male",
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history": ["hypertension"],
    "current_medications": ["lisinopril"],
    "allergies": ["penicillin"]
  }'
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_diagnosis_agent.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔒 Security & Compliance

This system implements several security measures:

- **HIPAA Compliance**: Patient data anonymization and encryption
- **Authentication**: Bearer token authentication for API access
- **Audit Logging**: All diagnoses and consultations are logged
- **Safety Validation**: Automatic checks for drug interactions and contraindications
- **Human Review Required**: All AI recommendations flagged for professional review

## 📊 Data Sources

To use this system effectively, you should collect and prepare:

1. **Medical Literature**
   - Research papers from PubMed, medical journals
   - Clinical practice guidelines
   - Treatment protocols

2. **Patient Records** (Anonymized)
   - Symptom descriptions
   - Diagnosis and treatment outcomes
   - Follow-up data

3. **Drug Databases**
   - DrugBank
   - RxNorm
   - FDA drug labels

4. **Clinical Trials**
   - ClinicalTrials.gov data
   - Trial outcomes and protocols

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- LLM model selection and parameters
- RAG retrieval settings
- API configuration
- Security settings
- Logging preferences

## 📈 Performance Optimization

For production deployment:

1. **Use GPU acceleration** for faster inference
2. **Implement caching** for frequently accessed knowledge
3. **Batch processing** for multiple diagnoses
4. **Load balancing** for high-traffic scenarios
5. **Monitor and log** all system performance metrics

## 🤝 Contributing

This is a research/educational project. Contributions should focus on:

- Improving diagnostic accuracy
- Adding new medical knowledge sources
- Enhancing safety validation
- Better testing and validation

## 📄 License

This project is for educational and research purposes only.

## ⚠️ Ethical Considerations

- Always obtain proper consent for patient data usage
- Ensure data anonymization and privacy
- Use only for assisting licensed medical professionals
- Follow all applicable medical regulations
- Never use as a replacement for professional medical judgment

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.

## 🙏 Acknowledgments

This system uses:
- LangChain for agent orchestration
- ChromaDB for vector storage
- Transformers for LLM fine-tuning
- FastAPI for web services
- SciSpacy for medical NLP

---

**Remember: This is an AI assistant tool. Always consult qualified healthcare professionals for medical decisions.**
