# Architecture Documentation

## Overview

The AI-Powered Travel Itinerary Generator is built on AWS using a microservices architecture with the following design principles:

- **Scalability**: Auto-scaling at application and data layers
- **High Availability**: Multi-AZ deployment
- **Security**: Defense in depth with multiple security layers
- **Cost Optimization**: Right-sized resources with auto-scaling
- **Observability**: Comprehensive logging and monitoring

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Route 53 (DNS) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Application LB  │
                    │   (Public)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  ECS Tasks    │   │  ECS Tasks    │   │  ECS Tasks    │
│  (Private)    │   │  (Private)    │   │  (Private)    │
│  AZ-1         │   │  AZ-2         │   │  AZ-3         │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  RDS Primary  │   │ ElastiCache   │   │  OpenSearch   │
│  (Private)    │   │  Redis        │   │  Cluster      │
│  AZ-1         │   │  (Private)    │   │  (Private)    │
└───────┬───────┘   └───────────────┘   └───────────────┘
        │
┌───────▼───────┐
│  RDS Standby  │
│  (Private)    │
│  AZ-2         │
└───────────────┘
```

## Component Details

### 1. Network Layer

#### VPC Configuration
- **CIDR**: 10.0.0.0/16
- **Availability Zones**: 3 (for high availability)
- **Subnets**:
  - Public: 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24
  - Private: 10.0.100.0/24, 10.0.101.0/24, 10.0.102.0/24

#### Internet Connectivity
- **Internet Gateway**: For public subnet internet access
- **NAT Gateways**: 3 (one per AZ) for private subnet outbound internet
- **VPC Endpoints**: For AWS service access without internet (optional)

### 2. Application Layer

#### ECS Fargate
- **Container Platform**: AWS Fargate (serverless)
- **Task Definition**:
  - CPU: 1024 units (1 vCPU)
  - Memory: 2048 MB (2 GB)
  - Port: 8000
- **Service Configuration**:
  - Desired Count: 2 (minimum)
  - Auto-scaling: 1-10 tasks based on CPU/Memory
  - Deployment: Rolling update with circuit breaker

#### Auto Scaling Policies
- **CPU-based**: Target 70% utilization
- **Memory-based**: Target 80% utilization
- **Scale-out**: Add task when threshold exceeded for 2 minutes
- **Scale-in**: Remove task when below threshold for 5 minutes

#### Load Balancing
- **Type**: Application Load Balancer (Layer 7)
- **Health Checks**:
  - Path: /health
  - Interval: 30 seconds
  - Timeout: 5 seconds
  - Healthy threshold: 2
  - Unhealthy threshold: 3

### 3. Data Layer

#### RDS PostgreSQL
- **Engine**: PostgreSQL 15.4
- **Instance Class**: db.t3.medium (dev), db.r6g.xlarge (prod)
- **Storage**:
  - Type: GP3
  - Size: 100 GB (auto-scaling to 200 GB)
  - IOPS: 3000
- **High Availability**:
  - Multi-AZ deployment (optional)
  - Automated backups (7-day retention)
  - Manual snapshots
- **Security**:
  - Encryption at rest (AES-256)
  - Encryption in transit (SSL/TLS)
  - Private subnet only

#### ElastiCache Redis
- **Engine**: Redis 7.0
- **Node Type**: cache.t3.medium (dev), cache.r6g.large (prod)
- **Configuration**:
  - Number of nodes: 1 (dev), 2+ (prod)
  - Snapshot retention: 5 days
  - Maintenance window: Monday 5:00-7:00 AM
- **Use Cases**:
  - Session management
  - API response caching
  - Rate limiting
  - Temporary data storage

#### OpenSearch
- **Engine**: OpenSearch 2.11
- **Instance Type**: t3.medium.search (dev), r6g.xlarge.search (prod)
- **Cluster Configuration**:
  - Data nodes: 2
  - Zone awareness: Enabled
  - EBS storage: 100 GB GP3 per node
- **Features**:
  - Vector search for RAG
  - Full-text search
  - Analytics and aggregations
- **Security**:
  - Fine-grained access control
  - Encryption at rest and in transit
  - VPC deployment

#### S3 Buckets

**Data Bucket**
- Purpose: Travel guides, reviews, user data
- Versioning: Enabled
- Encryption: AES-256
- Access: Private

**Models Bucket**
- Purpose: ML models, embeddings
- Versioning: Enabled
- Encryption: AES-256
- Access: Private

**Logs Bucket**
- Purpose: Application and access logs
- Lifecycle: 30d → IA, 90d → Glacier, 365d → Delete
- Encryption: AES-256
- Access: Private

### 4. AI/ML Components

#### OpenAI Integration
- **API**: OpenAI GPT-4/GPT-3.5
- **Use Cases**:
  - Itinerary generation
  - Natural language understanding
  - Recommendation explanation
- **Features**:
  - Fine-tuning on travel data
  - Prompt engineering
  - Context management

#### RAG Implementation
- **Vector Database**: OpenSearch with k-NN plugin
- **Embedding Model**: text-embedding-ada-002 or custom
- **Pipeline**:
  1. User query → Embedding
  2. Vector search in OpenSearch
  3. Retrieve relevant documents
  4. Augment LLM prompt with context
  5. Generate response

#### SageMaker (Optional)
- **Purpose**: Custom ML models
- **Use Cases**:
  - Preference prediction
  - Demand forecasting
  - Price optimization
- **Deployment**:
  - Real-time endpoint
  - Instance: ml.m5.xlarge
  - Auto-scaling: 1-5 instances

### 5. Serverless Components

#### Lambda Functions
- **Data Processor**:
  - Trigger: S3 uploads
  - Runtime: Python 3.11
  - Memory: 1024 MB
  - Timeout: 5 minutes
  - Purpose: Process uploaded travel data

### 6. Security

#### Network Security
```
┌─────────────────────────────────────────┐
│ Security Group: ALB                     │
│ Inbound:  80, 443 from 0.0.0.0/0       │
│ Outbound: All to ECS SG                │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Security Group: ECS                     │
│ Inbound:  8000 from ALB SG             │
│ Outbound: 5432 to RDS SG               │
│           6379 to Cache SG             │
│           443 to OpenSearch SG         │
└─────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────────┐
    ▼             ▼              ▼
┌────────┐  ┌─────────┐  ┌──────────────┐
│ RDS SG │  │Cache SG │  │OpenSearch SG │
│ 5432   │  │ 6379    │  │ 443          │
└────────┘  └─────────┘  └──────────────┘
```

#### IAM Roles

**ECS Task Execution Role**
- Pull images from ECR
- Write to CloudWatch Logs
- Access Secrets Manager

**ECS Task Role**
- Read/Write to S3 buckets
- Invoke SageMaker endpoints
- Access OpenSearch

**Lambda Execution Role**
- VPC access
- S3 read/write
- CloudWatch Logs

#### Secrets Management
- **Database credentials**: Secrets Manager
- **API keys**: Secrets Manager
- **SSL certificates**: ACM (optional)

### 7. Monitoring and Logging

#### CloudWatch Logs
- `/ecs/travel-ai-dev`: ECS container logs
- `/aws/lambda/data-processor`: Lambda logs
- `/aws/rds/instance/...`: Database logs

#### CloudWatch Metrics
- ECS: CPU, Memory, Task count
- RDS: Connections, CPU, Storage
- ALB: Request count, Latency, 5xx errors
- OpenSearch: CPU, Memory, Search latency

#### Alarms
- ECS CPU > 80%
- RDS CPU > 80%
- ALB 5xx errors > 10/minute
- OpenSearch cluster red status

### 8. Data Flow

#### User Request Flow
```
1. User → ALB → ECS Task
2. ECS Task checks Redis cache
3. If miss, query RDS for user data
4. Generate embeddings for user query
5. Search OpenSearch for relevant documents
6. Call OpenAI API with context
7. Generate itinerary
8. Store in RDS
9. Cache in Redis
10. Return to user
```

#### Data Processing Flow
```
1. User uploads file → S3
2. S3 triggers Lambda
3. Lambda processes file
4. Extract/transform data
5. Generate embeddings
6. Store in OpenSearch
7. Update metadata in RDS
```

## Scalability Considerations

### Horizontal Scaling
- ECS tasks: Auto-scale 1-10 based on load
- RDS: Read replicas for read-heavy workloads
- OpenSearch: Add data nodes for storage/performance
- ElastiCache: Add nodes/shards for capacity

### Vertical Scaling
- Increase ECS task size (CPU/Memory)
- Upgrade RDS instance class
- Increase OpenSearch instance size
- Larger ElastiCache nodes

## Cost Optimization

### Strategies
1. **Use Fargate Spot** for non-critical tasks
2. **RDS Reserved Instances** for production
3. **S3 Lifecycle Policies** for old data
4. **Right-sizing** based on CloudWatch metrics
5. **Auto-scaling** to match demand
6. **Data transfer optimization** using VPC endpoints

### Estimated Costs (Development)
- ECS Fargate: $50/month
- RDS t3.medium: $60/month
- ElastiCache: $35/month
- OpenSearch: $120/month
- Data transfer: $20/month
- **Total**: ~$285/month

## Disaster Recovery

### Backup Strategy
- **RDS**: Automated daily backups (7-day retention)
- **S3**: Versioning enabled
- **OpenSearch**: Daily snapshots to S3
- **Terraform State**: S3 with versioning

### Recovery Procedures
- **RDS**: Point-in-time restore
- **S3**: Object versioning restore
- **OpenSearch**: Snapshot restore
- **Infrastructure**: Terraform apply from backup state

### RTO/RPO Targets
- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 24 hours

## Future Enhancements

1. **Multi-region deployment** for global availability
2. **CDN** (CloudFront) for static assets
3. **API Gateway** for API management
4. **EventBridge** for event-driven architecture
5. **Step Functions** for complex workflows
6. **Kinesis** for real-time data streaming
7. **Aurora Serverless** for variable workloads
8. **AppSync** for GraphQL API
