# Supply Chain Management RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system for predictive supply chain and inventory management using LLMs, vector databases, and real-time data integration.

## Overview

This project implements an AI-powered supply chain optimization system that combines:
- **RAG Architecture**: Retrieval-Augmented Generation for intelligent insights
- **Demand Forecasting**: Predictive analytics for inventory requirements
- **Real-time Monitoring**: Live tracking of supply chain metrics
- **Optimization Engine**: Automated recommendations for inventory and logistics

## Features

### 1. Data Collection & Processing
- Synthetic supply chain data generation
- Historical inventory tracking
- Supplier performance metrics
- Logistics and shipment data

### 2. RAG Implementation
- FAISS vector store for semantic search
- Sentence-transformers embeddings
- Context-aware document retrieval
- Knowledge base integration

### 3. Supply Chain Intelligence Agent
- **Inventory Analysis**: Real-time stock level monitoring
- **Demand Prediction**: 7-14 day demand forecasting
- **Reorder Optimization**: Economic Order Quantity (EOQ) calculation
- **Risk Assessment**: Proactive identification of supply chain risks
- **Supplier Evaluation**: Reliability and cost analysis

### 4. Real-time Capabilities
- Market trend monitoring
- Dynamic vector store updates
- Supplier status tracking
- Disruption detection

### 5. Visualization & Reporting
- Interactive dashboards
- Demand forecasting charts
- Risk assessment visualizations
- Performance metrics

## Installation

### Prerequisites
- Python 3.8+
- Jupyter Notebook or JupyterLab
- 4GB+ RAM recommended

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-execution

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter Notebook
jupyter notebook supply_chain_rag_system.ipynb
```

## Usage

### Quick Start

1. **Run All Cells**: Execute the notebook sequentially to:
   - Generate synthetic supply chain data
   - Build the RAG vector store
   - Initialize the optimization agent
   - View dashboards and insights

2. **Interactive Queries**:
```python
# Ask questions about your supply chain
query_supply_chain("What products need immediate reordering?")
query_supply_chain("Which supplier has the best reliability score?")
query_supply_chain("What are current supply chain risks?")
```

3. **Demand Forecasting**:
```python
# Predict future demand
predictions = agent.predict_demand('Electronics_Component_A', days_ahead=14)
```

4. **Inventory Optimization**:
```python
# Get reorder recommendations
optimization = agent.optimize_reorder('Raw_Material_Steel')
print(f"Reorder Point: {optimization['reorder_point']}")
print(f"Order Quantity: {optimization['order_quantity']}")
```

5. **Risk Assessment**:
```python
# Identify supply chain risks
risks = agent.identify_risks()
display(risks)
```

## System Components

### Data Layer
- **Inventory Data**: Stock levels, demand, reorder points
- **Supplier Data**: Reliability scores, costs, lead times
- **Logistics Data**: Shipments, routes, delivery status
- **Knowledge Base**: Best practices and optimization strategies

### RAG System
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Retrieval**: Top-K semantic search with configurable K
- **Documents**: 200+ supply chain documents

### Intelligence Agent
- **Forecasting**: Moving average with trend analysis
- **Optimization**: EOQ, safety stock, reorder point calculation
- **Risk Detection**: Low stock, supplier reliability, logistics delays
- **Recommendations**: RAG-powered insights and best practices

## Configuration

Edit the `Config` class in the notebook to customize:

```python
class Config:
    # API Keys
    OPENAI_API_KEY = 'your-key-here'  # For production LLM
    ANTHROPIC_API_KEY = 'your-key-here'  # Alternative LLM

    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RETRIEVAL = 5

    # Paths
    DATA_DIR = './supply_chain_data'
    VECTOR_STORE_DIR = './vector_stores'
```

## Production Deployment

### Using Real LLMs

Replace the `MockLLM` with actual LLM integration:

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4",
    api_key=config.OPENAI_API_KEY
)

# Or Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    api_key=config.ANTHROPIC_API_KEY
)
```

### Real Data Integration

Connect to actual data sources:

```python
# Example: PostgreSQL connection
import psycopg2
conn = psycopg2.connect(
    host="your-db-host",
    database="supply_chain_db",
    user="username",
    password="password"
)

# Load real inventory data
inventory_df = pd.read_sql("SELECT * FROM inventory", conn)
```

### API Deployment

Deploy as a REST API using FastAPI:

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/predict-demand")
def predict_demand(product: str, days: int):
    return agent.predict_demand(product, days_ahead=days)

@app.get("/risks")
def get_risks():
    return agent.identify_risks().to_dict()
```

## Performance Metrics

The system evaluates performance using:

- **Forecast Accuracy**: MAE, RMSE, MAPE
- **Inventory KPIs**: Turnover rate, fill rate, stockout events
- **Retrieval Quality**: Precision@K for RAG system
- **Response Time**: Query processing speed

## Next Steps

### Immediate Improvements
1. [ ] Integrate real LLM (OpenAI GPT-4 or Anthropic Claude)
2. [ ] Connect to production databases
3. [ ] Implement advanced forecasting (LSTM, Prophet)
4. [ ] Add authentication and access control

### Advanced Features
1. [ ] Multi-agent collaboration system
2. [ ] What-if scenario simulation
3. [ ] Automated purchase order generation
4. [ ] Integration with IoT sensors
5. [ ] Blockchain for supply chain transparency

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│              (Jupyter Notebook / API)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Supply Chain Agent                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Inventory  │  │   Demand     │  │     Risk     │     │
│  │   Analysis   │  │  Forecasting │  │  Assessment  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   RAG System                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Vector Store (FAISS)                      │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │  │
│  │  │Inventory│ │Supplier│ │Logistics│ │Knowledge│   │  │
│  │  │  Docs   │ │  Docs  │ │  Docs   │ │  Base   │   │  │
│  │  └────────┘  └────────┘  └────────┘  └────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Data Sources                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Inventory │  │Suppliers │  │Logistics │  │  Market  │  │
│  │   DB     │  │   APIs   │  │ Tracking │  │  Feeds   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Technologies

- **LangChain**: LLM orchestration and RAG framework
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **Pandas/NumPy**: Data processing
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning utilities

## Evaluation Results

Based on synthetic data:
- Documents in Vector Store: 200+
- Products Tracked: 8
- Suppliers Monitored: 4
- Warehouses: 4
- Historical Data: 365 days
- Real-time Update Capability: Yes

## Contributing

Contributions are welcome! Areas for improvement:
- Advanced ML models for demand forecasting
- Real-time data connectors
- Enhanced visualization dashboards
- Multi-objective optimization
- Integration with ERP systems

## License

MIT License - see LICENSE file for details

## References

- LangChain Documentation: https://python.langchain.com/
- FAISS: https://github.com/facebookresearch/faiss
- Supply Chain Best Practices: APICS, CSCMP guidelines
- RAG Architecture: https://arxiv.org/abs/2005.11401

## Contact

For questions or support, please open an issue in the repository.

---

**Note**: This is a demonstration system using synthetic data. For production use, integrate with real data sources and deploy appropriate security measures.
