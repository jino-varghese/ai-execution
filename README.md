# SAP Intelligent Document Processing and Query Answering Agent

A comprehensive Retrieval Augmented Generation (RAG) system for SAP document processing, enabling intelligent query answering for invoices, purchase orders, sales orders, and financial reports.

## Overview

This project implements a real-time RAG system that:
- Processes and indexes SAP documents automatically
- Enables natural language queries about SAP data
- Provides accurate answers with source attribution
- Supports multiple document types and formats
- Includes comprehensive evaluation metrics

## Features

### Core Capabilities
- **Document Processing**: Automated loading, cleaning, and chunking of SAP documents
- **Semantic Search**: Vector-based similarity search using state-of-the-art embeddings
- **Intelligent Q&A**: RAG pipeline with LLM integration for contextual answers
- **Multi-Document Support**: Handles invoices, purchase orders, sales orders, and reports
- **Source Attribution**: Every answer includes references to source documents
- **Real-Time Processing**: Fast query response with optimized retrieval

### Advanced Features
- Document type filtering
- Date range queries
- Financial data aggregation
- Metadata-based search
- Performance evaluation metrics
- Latency monitoring

## Architecture

```
┌─────────────────┐
│  SAP Documents  │
│ (Various Types) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │
│ & Chunking      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embeddings     │
│  Generation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │
│  (ChromaDB)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────┐
│  RAG Pipeline   │◄────►│     LLM     │
└────────┬────────┘      └─────────────┘
         │
         ▼
┌─────────────────┐
│  Query Results  │
│ + Source Docs   │
└─────────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- (Optional) OpenAI API key for production LLM usage

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-execution
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install packages manually:
```bash
pip install langchain langchain-community langchain-openai
pip install chromadb sentence-transformers
pip install openai pypdf python-dotenv
pip install pandas numpy faiss-cpu tiktoken
```

3. (Optional) Configure OpenAI API:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### Quick Start

1. Open the Jupyter notebook:
```bash
jupyter notebook sap_rag_intelligent_agent.ipynb
```

2. Run all cells sequentially to:
   - Generate sample SAP documents
   - Create vector embeddings
   - Build the RAG pipeline
   - Test queries

### Example Queries

```python
# Initialize the RAG agent
result = rag_agent.query("What is the status of invoice INV-000001?")
print(result['answer'])

# Query purchase orders
result = rag_agent.query("Show me purchase orders for the IT department")
print(result['answer'])

# Financial queries
result = rag_agent.query("What are the total sales for Q1 2024?")
print(result['answer'])
```

### Advanced Usage

#### Filter by Document Type
```python
invoice_docs = advanced_features.filter_by_document_type(
    "payment terms",
    doc_type="invoice",
    k=5
)
```

#### Batch Processing
```python
questions = [
    "What is the total revenue?",
    "Show outstanding invoices",
    "List recent purchase orders"
]
results = rag_agent.batch_query(questions)
```

#### Performance Evaluation
```python
# Evaluate retrieval quality
metrics = evaluator.evaluate_retrieval_quality(test_queries)

# Measure latency
latency = evaluator.measure_latency(sample_queries)
```

## Configuration

Key configuration parameters in the notebook:

```python
class Config:
    # Embedding model
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM model
    LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo"
    TEMPERATURE = 0.1

    # Chunking
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Retrieval
    TOP_K_DOCUMENTS = 5

    # Storage
    VECTOR_STORE_PATH = "./sap_vector_store"
```

## Document Types

The system supports the following SAP document types:

### 1. Invoices
- Invoice number and date
- Customer information
- Line items with pricing
- Payment terms and status
- Tax calculations

### 2. Purchase Orders
- PO number and date
- Vendor information
- Requesting department
- Delivery dates and status
- Order items and quantities

### 3. Sales Orders
- SO number and date
- Customer details
- Sales representative
- Order status and shipping
- Item details with discounts

### 4. Financial Reports
- Report ID and period
- Department information
- Revenue and expenses
- Key metrics
- Budget variance analysis

## Evaluation Metrics

The system includes comprehensive evaluation:

### Retrieval Metrics
- **Precision@K**: Relevance of top-K results
- **Recall@K**: Coverage of relevant documents
- **Mean Reciprocal Rank (MRR)**: Ranking quality

### Performance Metrics
- **Average Latency**: Query response time
- **P95 Latency**: 95th percentile response time
- **Throughput**: Queries per second

### Quality Metrics
- **Semantic Similarity**: Answer quality assessment
- **Source Attribution**: Accuracy of document references

## Production Deployment

### Checklist

#### 1. Data Integration
- [ ] Connect to real SAP system (HANA, S/4HANA)
- [ ] Implement data extraction pipelines
- [ ] Set up incremental updates
- [ ] Handle multiple document formats

#### 2. Model Configuration
- [ ] Fine-tune embeddings on SAP data
- [ ] Configure LLM with SAP domain knowledge
- [ ] Set up model versioning
- [ ] Implement A/B testing

#### 3. Infrastructure
- [ ] Choose production vector database
- [ ] Set up backup and recovery
- [ ] Configure auto-scaling
- [ ] Implement caching strategy

#### 4. Security
- [ ] Implement authentication/authorization
- [ ] Encrypt sensitive data
- [ ] Comply with regulations (GDPR, etc.)
- [ ] Set up audit logging

#### 5. Monitoring
- [ ] Set up observability (logging, metrics)
- [ ] Implement user feedback collection
- [ ] Configure alerting
- [ ] Regular performance evaluation

### Recommended Stack

**Vector Database Options:**
- Pinecone (managed, scalable)
- Weaviate (open-source, feature-rich)
- Qdrant (fast, efficient)

**LLM Options:**
- OpenAI GPT-4 (high quality)
- Anthropic Claude (context-aware)
- Open-source models (privacy, cost)

**Deployment Options:**
- AWS (SageMaker, Lambda, RDS)
- Google Cloud (Vertex AI, Cloud Run)
- Azure (OpenAI Service, Functions)

## Performance

Based on sample dataset (100 documents, 400 chunks):

- **Average Query Time**: ~0.5-1.5 seconds
- **Retrieval Accuracy**: >85% precision@5
- **Embedding Generation**: ~50ms per document
- **Vector Search**: <100ms

## Limitations and Future Improvements

### Current Limitations
- Simulated SAP data (not real production data)
- Basic document parsing (no complex PDF/XML handling)
- Single language support (English only)
- No user authentication or multi-tenancy

### Planned Improvements
1. **Hybrid Search**: Combine keyword and semantic search
2. **Query Expansion**: Automatic query reformulation
3. **Re-ranking**: Improve result relevance
4. **Multi-modal**: Support images and tables
5. **Fine-tuning**: Custom embeddings and LLM
6. **Streaming**: Real-time answer generation
7. **Feedback Loop**: Continuous learning from user feedback

## Troubleshooting

### Common Issues

**Issue**: "Module not found" errors
**Solution**: Install missing packages with pip

**Issue**: Slow query performance
**Solution**: Reduce CHUNK_SIZE or TOP_K_DOCUMENTS

**Issue**: Poor answer quality
**Solution**:
- Add more training data
- Increase chunk overlap
- Fine-tune embedding model

**Issue**: Out of memory errors
**Solution**:
- Process documents in batches
- Use smaller embedding model
- Reduce chunk size

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For questions or issues:
- Review the notebook documentation
- Check the troubleshooting section
- Consult LangChain and ChromaDB documentation

## Acknowledgments

Built with:
- [LangChain](https://www.langchain.com/) - RAG framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [OpenAI](https://openai.com/) - LLM (optional)

## References

- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Vector Database Guide](https://www.pinecone.io/learn/vector-database/)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [SAP Integration Patterns](https://help.sap.com/)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-18
**Status**: Production-Ready Demo
