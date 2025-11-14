# Personalized Shopping Assistant using LLMs and RAGs

A comprehensive AI-powered shopping assistant that provides personalized product recommendations using Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) technology.

## Overview

This project demonstrates a complete implementation of an intelligent e-commerce recommendation system that combines:

- **RAG (Retrieval-Augmented Generation)** for semantic product search
- **LLM Integration** for understanding customer preferences
- **Multi-factor Recommendation Algorithm** for personalized suggestions
- **Real-time Stock Management** and availability checks
- **Dynamic Promotional Offers** based on customer loyalty
- **Comprehensive Evaluation Framework** for measuring system effectiveness

## Features

### 1. LLM Fine-Tuning on Product Descriptions
- Understanding product features, attributes, and customer reviews
- Semantic analysis of product descriptions
- Customer preference extraction and analysis

### 2. RAG for Product Search
- Real-time product information retrieval
- Vector-based semantic search using ChromaDB
- Efficient embedding generation with SentenceTransformers
- Context-aware product matching

### 3. Personalized Recommendation Agent
- Multi-factor scoring algorithm considering:
  - Category preferences (30%)
  - Price alignment (20%)
  - Product ratings (20%)
  - RAG relevance scores (30%)
- Purchase history analysis
- Browsing behavior tracking
- Loyalty-based promotions

### 4. Evaluation Metrics
- Category relevance measurement
- Price alignment scoring
- Product quality assessment
- Recommendation diversity analysis
- Customer satisfaction metrics

## Project Structure

```
ai-execution/
├── shopping_assistant.ipynb    # Main Jupyter notebook
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Jupyter Notebook

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

3. Launch Jupyter Notebook:
```bash
jupyter notebook shopping_assistant.ipynb
```

## Usage

### Running the Notebook

The notebook is organized into the following sections:

1. **Setup and Installation** - Install required packages
2. **Data Collection** - Generate sample product catalog and customer data
3. **RAG System Implementation** - Set up vector database and search functionality
4. **LLM Integration** - Initialize language models for understanding
5. **Recommendation Agent** - Build the core recommendation engine
6. **Evaluation** - Test and measure system performance
7. **Interactive Demo** - Try the system with custom queries
8. **Advanced Features** - Stock management and promotions
9. **Summary** - Performance metrics and insights
10. **Next Steps** - Future improvements and enhancements

### Quick Start Example

```python
# Initialize the shopping agent
shopping_agent = PersonalizedShoppingAgent(analyzer, products_df, purchase_history_df)

# Get recommendations for a customer
recommendations = shopping_agent.get_recommendations(
    customer_id="C001",
    query="fitness equipment",
    n_recommendations=5
)

# Display recommendations
shopping_agent.display_recommendations("C001", query="fitness products")
```

## System Architecture

### Components

1. **Embedding Model**: `all-MiniLM-L6-v2` from SentenceTransformers
2. **Vector Database**: ChromaDB for efficient similarity search
3. **LLM**: DistilGPT2 for text generation and understanding
4. **Recommendation Engine**: Custom multi-factor algorithm

### Data Flow

```
Customer Query → Profile Analysis → RAG Search → Score Calculation → Ranking → Recommendations
```

## Sample Data

The notebook includes a comprehensive dataset:

- **12 Products** across 6 categories
- **4 Customer Profiles** with different preferences
- **10 Purchase History Records**
- **5 Browsing History Entries**

Categories include:
- Electronics
- Wearables
- Sports & Fitness
- Furniture
- Food & Beverages
- Kitchen Appliances
- Home & Bedding
- Home & Office

## Performance Metrics

The system achieves:
- **High Category Relevance**: Matches customer preferred categories
- **Strong Price Alignment**: Recommends products within customer's typical price range
- **Quality Products**: Average rating of recommended products > 4.4/5
- **Good Diversity**: Recommendations span multiple relevant categories

## Evaluation Results

The evaluation framework measures:

1. **Category Relevance**: How well recommendations match preferred categories
2. **Price Alignment**: Alignment with customer's typical spending
3. **Average Rating**: Quality of recommended products
4. **Diversity Score**: Variety in recommendations
5. **Overall Recommendation Score**: Combined performance metric

## Advanced Features

### Stock Availability
- Real-time stock checking
- Low stock alerts
- Out-of-stock filtering

### Promotional Offers
- Loyalty discounts (10% for 3+ purchases)
- Category preference bonuses (15%)
- Top-rated product promotions (5%)

### Personalization Factors
- Purchase history analysis
- Browsing behavior tracking
- Explicit preference matching
- Implicit feature detection

## Future Enhancements

### Planned Improvements

1. **Advanced LLM Integration**
   - Fine-tune on product reviews
   - Conversational product discovery
   - Sentiment analysis

2. **Enhanced RAG System**
   - Multi-modal search (text + images)
   - Real-time inventory sync
   - Competitor pricing integration

3. **Recommendation Algorithm**
   - Collaborative filtering
   - Temporal pattern analysis
   - Social proof signals

4. **Production Features**
   - REST API endpoints
   - Caching layer
   - A/B testing framework
   - Real-time monitoring

## Technologies Used

- **Python 3.8+**
- **Pandas & NumPy** - Data manipulation
- **SentenceTransformers** - Text embeddings
- **ChromaDB** - Vector database
- **Transformers** - LLM integration
- **Scikit-learn** - Machine learning utilities
- **Matplotlib** - Visualization
- **Jupyter** - Interactive development

## Use Cases

This system is designed for:

- **E-commerce Platforms** - Product recommendations
- **Retail Websites** - Personalized shopping experiences
- **Marketplace Applications** - Customer-specific suggestions
- **Mobile Shopping Apps** - On-the-go recommendations

## Key Insights

1. **RAG Effectiveness**: Semantic search significantly improves product discovery
2. **Personalization Impact**: Multi-factor scoring enhances recommendation relevance
3. **Customer Profiling**: Purchase history is a strong signal for preferences
4. **Balance**: System maintains good balance between personalization and diversity

## Testing

The notebook includes comprehensive testing:

- Unit tests for recommendation algorithm
- Integration tests for RAG system
- Evaluation metrics for all customers
- Interactive demos with various queries

## Contributing

This is an educational project demonstrating LLM and RAG capabilities in e-commerce.

## License

MIT License - Feel free to use and modify for your projects.

## Contact

For questions or feedback, please open an issue in the repository.

## Acknowledgments

- HuggingFace Transformers library
- ChromaDB team
- SentenceTransformers project

---

**Note**: This is a demonstration project with sample data. For production use, integrate with real product catalogs, customer databases, and implement proper security measures.
