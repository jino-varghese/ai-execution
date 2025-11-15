# AI-Powered Travel Itinerary Generator

An intelligent travel assistant that generates personalized travel itineraries using LLMs, fine-tuning, and Retrieval Augmented Generation (RAG).

## Project Overview

This project implements a Tourism and Hospitality AI application that:
- **Fine-tunes LLMs** on travel guides, reviews, and historical travel itineraries
- **Uses RAG** to retrieve real-time information on destinations, hotels, attractions, and events
- **Generates custom itineraries** based on user preferences and constraints
- **Provides recommendations** for activities, restaurants, and experiences

## Architecture

The application is deployed on AWS using a microservices architecture:

### Core Components

1. **Application Layer** (ECS Fargate)
   - Containerized Python/FastAPI application
   - Auto-scaling based on CPU/Memory
   - Deployed across multiple availability zones

2. **Data Storage**
   - **RDS PostgreSQL**: User data, itineraries, bookings
   - **S3 Buckets**: Travel guides, ML models, user uploads
   - **ElastiCache Redis**: Session management and caching

3. **AI/ML Components**
   - **OpenSearch**: Vector database for RAG implementation
   - **SageMaker** (Optional): Custom ML model hosting
   - **LLM Integration**: OpenAI API or fine-tuned models

4. **Networking**
   - VPC with public/private subnets across 3 AZs
   - Application Load Balancer for traffic distribution
   - NAT Gateways for outbound internet access

## Project Structure

```
.
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main Terraform configuration
│   ├── variables.tf          # Variable definitions
│   ├── outputs.tf            # Output values
│   ├── terraform.tfvars.example
│   └── modules/              # Terraform modules
│       ├── vpc/              # VPC and networking
│       ├── security/         # Security groups
│       ├── s3/               # S3 buckets
│       ├── rds/              # PostgreSQL database
│       ├── elasticache/      # Redis cache
│       ├── opensearch/       # OpenSearch for RAG
│       ├── alb/              # Application Load Balancer
│       ├── ecs/              # ECS cluster and services
│       ├── secrets/          # Secrets Manager
│       ├── sagemaker/        # SageMaker endpoints
│       └── lambda/           # Lambda functions
├── app/                      # Application code
│   ├── src/                  # Source code
│   ├── models/               # ML models
│   ├── data/                 # Sample data
│   └── requirements.txt      # Python dependencies
├── docs/                     # Documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── ARCHITECTURE.md       # Architecture details
└── README.md                 # This file
```

## Features

### 1. LLM Fine-Tuning
- Fine-tuned on travel guides and itineraries
- Understands travel-related queries and preferences
- Generates contextually relevant recommendations

### 2. RAG Implementation
- Real-time information retrieval using OpenSearch
- Vector embeddings for semantic search
- Combines LLM knowledge with current data

### 3. Custom Itinerary Generation
- Personalized based on user preferences
- Budget-aware recommendations
- Time-optimized routes
- Activity suggestions based on interests

### 4. Real-time Integration
- Weather information
- Hotel availability
- Event calendars
- Restaurant recommendations

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.0
- AWS CLI configured
- Docker (for local development)

### Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-execution
   ```

2. **Configure Terraform variables**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Initialize and deploy infrastructure**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Deploy application**
   ```bash
   # Build and push Docker image
   # Update ECS service with new image
   ```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Configuration

### Required Variables

- `aws_region`: AWS region for deployment
- `db_password`: Database password (sensitive)
- `openai_api_key`: OpenAI API key (sensitive)
- `container_image`: Docker image for the application

### Optional Features

- **SageMaker**: Set `enable_sagemaker = true` for custom ML models
- **Lambda Processing**: Set `enable_lambda_processing = true` for data pipelines

## Cost Estimation

Estimated monthly costs (dev environment):
- ECS Fargate: ~$50-100
- RDS PostgreSQL: ~$50-80
- ElastiCache Redis: ~$30-50
- OpenSearch: ~$100-150
- Data Transfer: ~$20-40
- **Total**: ~$250-420/month

Production costs will be higher based on scale and traffic.

## Security

- All data encrypted at rest (S3, RDS, EBS)
- Encryption in transit (TLS/SSL)
- Private subnets for application and data layers
- Secrets managed via AWS Secrets Manager
- IAM roles with least privilege principle
- VPC endpoints for AWS services

## Development

### Local Development

```bash
cd app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Testing

```bash
pytest tests/
```

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture Details](docs/ARCHITECTURE.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Acknowledgments

- Built with AWS services
- Powered by OpenAI/LLM technology
- Uses OpenSearch for vector search
