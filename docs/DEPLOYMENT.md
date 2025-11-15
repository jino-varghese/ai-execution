# Deployment Guide

Complete guide for deploying the AI-Powered Travel Itinerary Generator to AWS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Infrastructure Deployment](#infrastructure-deployment)
4. [Application Deployment](#application-deployment)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Terraform** >= 1.0
  ```bash
  brew install terraform  # macOS
  # or download from https://www.terraform.io/downloads
  ```

- **AWS CLI** >= 2.0
  ```bash
  brew install awscli  # macOS
  # or download from https://aws.amazon.com/cli/
  ```

- **Docker** (for building images)
  ```bash
  brew install docker  # macOS
  # or download from https://www.docker.com/
  ```

### AWS Account Setup

1. **IAM User/Role** with permissions for:
   - EC2, VPC, ECS
   - RDS, ElastiCache
   - S3, Secrets Manager
   - OpenSearch, SageMaker (optional)
   - IAM, CloudWatch

2. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter AWS Access Key ID
   # Enter AWS Secret Access Key
   # Enter Default region (e.g., us-east-1)
   # Enter Default output format (json)
   ```

3. **Verify Configuration**
   ```bash
   aws sts get-caller-identity
   ```

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-execution
```

### 2. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
aws_region   = "us-east-1"
environment  = "dev"
project_name = "travel-ai"

# Database Configuration
db_password = "YourSecurePassword123!"  # Use a strong password

# API Keys
openai_api_key = "sk-your-openai-api-key"

# Container Configuration
container_image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:latest"
```

### 3. Configure Terraform Backend (Optional but Recommended)

For production, use S3 backend for state management:

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://your-terraform-state-bucket

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

Uncomment the backend configuration in `main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "travel-ai/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## Infrastructure Deployment

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Review Deployment Plan

```bash
terraform plan -out=tfplan
```

Review the plan carefully. It will create:
- VPC with 3 public and 3 private subnets
- NAT Gateways, Internet Gateway
- Security Groups
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- OpenSearch domain
- Application Load Balancer
- ECS cluster (without tasks initially)
- S3 buckets
- Secrets Manager secrets
- IAM roles and policies

### 3. Apply Infrastructure

```bash
terraform apply tfplan
```

This will take approximately 20-30 minutes to complete.

### 4. Save Outputs

```bash
terraform output > ../terraform-outputs.txt
```

## Application Deployment

### 1. Build Docker Image

```bash
cd ../app

# Build the Docker image
docker build -t travel-ai:latest .
```

### 2. Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name travel-ai

# Get login command
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### 3. Push Image to ECR

```bash
# Tag image
docker tag travel-ai:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:latest

# Push image
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:latest
```

### 4. Update ECS Service

If the image wasn't available during initial deployment:

```bash
cd ../terraform
terraform apply -var="container_image=123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:latest"
```

### 5. Verify Deployment

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Test the endpoint
curl http://<alb-dns-name>/health
```

## Post-Deployment Configuration

### 1. Initialize Database

```bash
# Connect to RDS via bastion or port forwarding
# Run database migrations
python manage.py migrate
```

### 2. Upload Travel Data to S3

```bash
# Upload travel guides, reviews, etc.
aws s3 sync ./data/travel-guides s3://travel-ai-dev-data-xxxxx/guides/
aws s3 sync ./data/reviews s3://travel-ai-dev-data-xxxxx/reviews/
```

### 3. Configure OpenSearch

```bash
# Create indices for vector search
python scripts/setup_opensearch.py

# Upload embeddings
python scripts/upload_embeddings.py
```

### 4. Set Up Monitoring

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard --dashboard-name travel-ai-dev \
  --dashboard-body file://cloudwatch-dashboard.json

# Set up alarms
aws cloudwatch put-metric-alarm --alarm-name ecs-high-cpu \
  --alarm-description "ECS CPU utilization high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## Monitoring and Maintenance

### CloudWatch Logs

```bash
# View ECS logs
aws logs tail /ecs/travel-ai-dev --follow

# View specific log stream
aws logs get-log-events \
  --log-group-name /ecs/travel-ai-dev \
  --log-stream-name ecs/app/<task-id>
```

### ECS Service Management

```bash
# Scale service
aws ecs update-service \
  --cluster travel-ai-dev-cluster \
  --service travel-ai-dev-service \
  --desired-count 4

# Force new deployment
aws ecs update-service \
  --cluster travel-ai-dev-cluster \
  --service travel-ai-dev-service \
  --force-new-deployment
```

### Database Backups

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier travel-ai-dev-db \
  --db-snapshot-identifier travel-ai-dev-snapshot-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier travel-ai-dev-db
```

### Updating Application

```bash
# Build new image
docker build -t travel-ai:v2 .

# Tag and push
docker tag travel-ai:v2 123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:v2
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/travel-ai:v2

# Update task definition and service
aws ecs update-service \
  --cluster travel-ai-dev-cluster \
  --service travel-ai-dev-service \
  --force-new-deployment
```

## Troubleshooting

### ECS Tasks Not Starting

1. Check CloudWatch logs:
   ```bash
   aws logs tail /ecs/travel-ai-dev --follow
   ```

2. Verify security groups allow traffic

3. Check task execution role permissions

### Database Connection Issues

1. Verify security group rules:
   ```bash
   aws ec2 describe-security-groups \
     --group-ids sg-xxxxx
   ```

2. Test connectivity from ECS task

3. Check database endpoint and credentials

### High Costs

1. Review resource usage:
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2024-01-01,End=2024-01-31 \
     --granularity MONTHLY \
     --metrics BlendedCost
   ```

2. Consider:
   - Reducing RDS instance size
   - Using reserved instances
   - Enabling auto-scaling
   - Cleaning up unused resources

### Performance Issues

1. Check ECS metrics:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ECS \
     --metric-name CPUUtilization \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Average
   ```

2. Enable auto-scaling if not already enabled

3. Optimize database queries and add indices

4. Increase Redis cache size

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Warning**: This will delete all data. Make sure to backup important data first.

## Next Steps

- Set up CI/CD pipeline
- Configure custom domain and SSL
- Implement monitoring and alerting
- Set up automated backups
- Configure WAF for security
- Implement rate limiting

## Support

For issues:
- Check CloudWatch logs
- Review AWS service health dashboard
- Consult AWS documentation
- Open an issue in the repository
