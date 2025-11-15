# System Architecture

## Overview

The AI-Powered Medical Diagnosis System is built with a modular architecture that separates concerns and allows for easy scaling and maintenance.

## Components

### 1. Medical Diagnosis Agent (`src/agents/`)

The core AI agent that orchestrates the diagnosis process.

**Key Features:**
- Uses LangChain for agent orchestration
- Multi-step reasoning with tool usage
- Memory for conversation context
- Safety validation at every step

**Tools Available:**
- RetrieveMedicalKnowledge: Access medical literature
- SearchDrugDatabase: Query drug information
- FindClinicalTrials: Search clinical trials
- AnalyzeSymptoms: NLP processing of symptoms
- CheckDrugInteractions: Validate medication safety

### 2. RAG System (`src/rag/`)

Retrieval Augmented Generation system for knowledge access.

**Architecture:**
```
Query → Embedding → Vector Search → Top-K Documents → Context
```

**Knowledge Sources:**
- Medical Literature (research papers, textbooks)
- Drug Databases (interactions, contraindications)
- Clinical Trials (latest protocols, outcomes)
- Treatment Guidelines (evidence-based protocols)

**Vector Database:**
- ChromaDB for persistent storage
- HuggingFace embeddings for semantic search
- Chunking strategy: 512 tokens with 50 token overlap

### 3. Data Processing Pipeline (`src/preprocessing/`)

Handles data preparation for fine-tuning and RAG indexing.

**Processing Steps:**
1. Data collection from various sources
2. Anonymization (HIPAA compliance)
3. Cleaning and normalization
4. Format conversion to JSONL
5. Validation and quality checks

**Output Formats:**
- Fine-tuning: Instruction-response pairs
- RAG: Document chunks with metadata

### 4. Fine-Tuning Module (`src/models/`)

Parameter-efficient fine-tuning using LoRA (Low-Rank Adaptation).

**Approach:**
- Uses PEFT (Parameter-Efficient Fine-Tuning)
- 8-bit quantization for memory efficiency
- LoRA for adapter training
- Only 0.1% of parameters are trainable

**Benefits:**
- Reduced memory requirements
- Faster training
- Smaller model checkpoints
- Easy to merge with base model

### 5. API Layer (`src/api/`)

RESTful API built with FastAPI.

**Endpoints:**
- `POST /api/v1/diagnosis` - Get diagnosis and recommendations
- `POST /api/v1/consultation` - Real-time medical consultation
- `POST /api/v1/knowledge/search` - Search medical knowledge
- `GET /api/v1/drug/{drug_name}` - Drug information lookup
- `GET /api/v1/clinical-trials/{condition}` - Clinical trial search

**Security:**
- Bearer token authentication
- Rate limiting
- CORS configuration
- Request validation with Pydantic

### 6. Utilities (`src/utils/`)

Supporting modules for safety and NLP.

**Safety Validator:**
- Patient data validation
- Diagnosis quality checks
- Drug interaction detection
- Allergy checking
- Age-appropriate treatment validation

**Medical NLP Processor:**
- Symptom analysis and extraction
- Medical entity recognition
- Terminology normalization
- Medication extraction

## Data Flow

### Diagnosis Request Flow

```
1. API receives patient data
   ↓
2. Safety validation
   ↓
3. Agent initialization
   ↓
4. Symptom analysis (NLP)
   ↓
5. Knowledge retrieval (RAG)
   ↓
6. Reasoning and diagnosis generation
   ↓
7. Treatment recommendations
   ↓
8. Safety validation
   ↓
9. Response with warnings
```

### Fine-Tuning Pipeline

```
1. Collect medical datasets
   ↓
2. Preprocess and anonymize
   ↓
3. Format as instruction-response pairs
   ↓
4. Load base LLM
   ↓
5. Apply LoRA adapters
   ↓
6. Train on medical data
   ↓
7. Save fine-tuned model
   ↓
8. Evaluate on test set
```

### RAG Indexing Flow

```
1. Load documents from source
   ↓
2. Split into chunks
   ↓
3. Generate embeddings
   ↓
4. Store in vector database
   ↓
5. Create metadata index
   ↓
6. Ready for retrieval
```

## Technology Stack

**Core AI:**
- LangChain: Agent orchestration
- Transformers: LLM inference
- PEFT: Efficient fine-tuning
- Sentence Transformers: Embeddings

**Data & Storage:**
- ChromaDB: Vector database
- PostgreSQL: Structured data (optional)
- Pandas: Data processing

**API & Web:**
- FastAPI: Web framework
- Uvicorn: ASGI server
- Pydantic: Data validation

**NLP:**
- spaCy: General NLP
- SciSpacy: Medical NLP
- MedSpacy: Clinical text processing

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer support
- Multiple agent instances

### Performance Optimization
- Vector database caching
- Embedding precomputation
- Batch processing
- GPU acceleration

### Monitoring
- Prometheus metrics
- Structured logging
- Performance tracking
- Error reporting

## Security & Compliance

### HIPAA Compliance
- Data encryption at rest and in transit
- Audit logging
- Access controls
- Data anonymization

### Safety Features
- Human review requirement
- Confidence thresholds
- Red flag detection
- Drug interaction checking

## Future Enhancements

1. **Multi-modal Support**: Image analysis (X-rays, MRIs)
2. **Reinforcement Learning**: Learn from physician feedback
3. **Federated Learning**: Train across institutions without sharing data
4. **Explainability**: Better reasoning transparency
5. **Real-time Updates**: Continuous learning from new research
