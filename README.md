# 🏥 AI-Powered Medical Diagnosis System

An educational AI-powered medical diagnosis system built with AWS Lambda and deployed using Terraform.

> **⚠️ DISCLAIMER**: This is an educational demo ONLY. NOT for actual medical use. Always consult qualified healthcare professionals for medical advice.

## 🚀 Features

- **AI Diagnosis Engine**: Analyzes patient symptoms using medical knowledge base
- **Treatment Recommendations**: Provides evidence-based treatment suggestions
- **RAG System**: Retrieves relevant medical research and clinical guidelines
- **Responsive Web Interface**: Modern, mobile-friendly UI
- **Serverless Architecture**: Fully serverless on AWS Lambda
- **Infrastructure as Code**: Complete Terraform deployment

## 📋 Prerequisites

Before deploying, ensure you have:

- **AWS Account** with appropriate permissions
- **AWS CLI** configured with credentials
- **Terraform** >= 1.0 installed ([Install Terraform](https://developer.hashicorp.com/terraform/downloads))
- **Git** for version control

### Verify Prerequisites

```bash
# Check AWS CLI
aws --version
aws sts get-caller-identity

# Check Terraform
terraform --version
```

## 🏗️ Architecture

```
┌─────────────────────┐
│   User's Browser    │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│ Lambda Function URL │ ← Public endpoint, CORS enabled
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AWS Lambda        │ ← Python 3.11, 256MB RAM, 30s timeout
│ Medical Diagnosis   │    - Serves web interface
│      System         │    - AI diagnosis engine
└──────────┬──────────┘    - Treatment recommendations
           │
           ▼
┌─────────────────────┐
│  CloudWatch Logs    │ ← Centralized logging
└─────────────────────┘
```

## 📦 Project Structure

```
AI-Powered-Medical-Diagnosis/
├── main.tf                      # Main Terraform configuration
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── terraform.tfvars.example     # Example configuration
├── deploy.sh                    # Automated deployment script
├── destroy.sh                   # Automated cleanup script
├── .gitignore                   # Git ignore rules
├── medical_diagnosis_lambda.py  # Lambda function code
├── medical_requirements.txt     # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended - 2 Minutes)

The easiest way to deploy using our automated script:

```bash
# Clone the repository
git clone <repository-url>
cd AI-Powered-Medical-Diagnosis

# Run the deployment script
./deploy.sh
```

The script will automatically:
- ✅ Check prerequisites (AWS CLI, Terraform)
- ✅ Verify AWS credentials
- ✅ Create terraform.tfvars if needed
- ✅ Initialize Terraform
- ✅ Show deployment plan
- ✅ Deploy to AWS
- ✅ Display application URL and access information

### Option 2: Manual Deployment (5 Minutes)

For more control over the deployment process:

#### Step 1: Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd AI-Powered-Medical-Diagnosis

# Create your variables file
cp terraform.tfvars.example terraform.tfvars

# (Optional) Edit terraform.tfvars to customize settings
nano terraform.tfvars
```

#### Step 2: Initialize Terraform

```bash
# Initialize Terraform (downloads required providers)
terraform init
```

#### Step 3: Review Deployment Plan

```bash
# See what resources will be created
terraform plan
```

### Step 4: Deploy to AWS

```bash
# Deploy the infrastructure
terraform apply

# Type 'yes' when prompted
```

### Step 5: Access Your Application

After deployment completes, Terraform will display:
- **Application URL**: Open this in your browser
- **CloudWatch Logs**: Monitor application logs
- **Lambda Console**: Manage your function

```bash
# Save the application URL
terraform output lambda_function_url
```

## 🔧 Configuration Options

Edit `terraform.tfvars` to customize your deployment:

### Basic Configuration

```hcl
# AWS region
aws_region = "us-east-1"

# Project name (affects resource naming)
project_name = "medical-diagnosis"

# Environment (dev, staging, prod)
environment = "dev"
```

### Lambda Configuration

```hcl
# Python runtime
lambda_runtime = "python3.11"

# Function timeout (seconds)
lambda_timeout = 30

# Memory allocation (MB)
lambda_memory_size = 256
```

### Security Configuration

```hcl
# Public access (true) or IAM auth (false)
enable_public_access = true

# CORS allowed origins
cors_allow_origins = ["*"]  # For production, specify exact domains
```

### Monitoring Configuration

```hcl
# Enable CloudWatch alarms
enable_alarms = true

# Error threshold
error_threshold = 5

# Duration threshold (ms)
duration_threshold = 25000

# Log retention (days)
log_retention_days = 7
```

## 📊 Monitoring & Debugging

### View Logs

```bash
# Tail CloudWatch logs
aws logs tail "/aws/lambda/medical-diagnosis-dev" --follow --region us-east-1
```

### Check Function Status

```bash
# Get Lambda function details
aws lambda get-function --function-name medical-diagnosis-dev --region us-east-1
```

### Test Function Manually

```bash
# Invoke the function with test payload
aws lambda invoke \
  --function-name medical-diagnosis-dev \
  --payload '{"requestContext":{"http":{"method":"POST"}},"body":"{\"symptoms\":[\"fever\",\"cough\",\"headache\"]}"}' \
  --region us-east-1 \
  response.json

cat response.json
```

## 💰 Cost Estimation

### AWS Free Tier (First 12 Months)
- **Lambda**: 1M requests/month FREE
- **Lambda**: 400,000 GB-seconds compute/month FREE
- **CloudWatch**: 5 GB logs/month FREE

### Estimated Monthly Cost
With moderate usage (< 10,000 requests/month):
- **Lambda**: $0.00 (within free tier)
- **CloudWatch**: $0.00 (within free tier)
- **Data Transfer**: $0.00 (within free tier)
- **Total**: **$0.00 - $1.00/month**

## 🔒 Security Best Practices

### For Development
✅ Public access enabled
✅ CORS set to allow all origins
✅ Basic CloudWatch logging

### For Production (Recommended)
- [ ] Set `enable_public_access = false` to require IAM authentication
- [ ] Configure specific CORS origins (not `*`)
- [ ] Enable CloudWatch alarms (`enable_alarms = true`)
- [ ] Add AWS WAF for DDoS protection
- [ ] Implement API Gateway with rate limiting
- [ ] Use AWS Secrets Manager for sensitive data
- [ ] Enable VPC integration if accessing private resources

## 🛠️ Common Operations

### Update Lambda Code

After modifying `medical_diagnosis_lambda.py`:

```bash
terraform apply
```

Terraform will automatically detect changes and redeploy.

### View All Outputs

```bash
terraform output
```

### Destroy Infrastructure

#### Option 1: Automated Cleanup (Recommended)

Use the automated script for safe destruction with multiple confirmations:

```bash
./destroy.sh
```

The script will:
- 🔍 Show all resources that will be destroyed
- ⚠️  Display multiple safety warnings
- 💾 Create backup of Terraform state
- 🗑️  Destroy all AWS resources
- ✅ Verify destruction
- 🧹 Optionally clean up local files

#### Option 2: Manual Cleanup

```bash
# Remove all AWS resources
terraform destroy

# Type 'yes' when prompted
```

### Change AWS Region

```bash
# Edit terraform.tfvars
aws_region = "us-west-2"

# Apply changes
terraform apply
```

## 🐛 Troubleshooting

### Issue: Terraform Init Fails

```bash
# Clear Terraform cache and reinitialize
rm -rf .terraform .terraform.lock.hcl
terraform init
```

### Issue: Lambda Permission Errors

```bash
# Check IAM role permissions
aws iam get-role --role-name medical-diagnosis-lambda-role-dev
```

### Issue: Function URL Not Working

```bash
# Verify function URL is enabled
terraform output lambda_function_url

# Check CORS configuration
aws lambda get-function-url-config --function-name medical-diagnosis-dev
```

### Issue: High Costs

```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=medical-diagnosis-dev \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

## 📚 Medical Knowledge Base

The system includes pre-configured medical knowledge for:

- **Influenza (Flu)**
- **Common Cold**
- **Hypertension**
- **Type 2 Diabetes**
- **Migraine**
- **Pneumonia**
- **Anxiety Disorder**
- **Gastritis**

Each condition includes:
- Symptom profiles
- Treatment recommendations
- Emergency warning signs
- Supporting research citations

## 🔬 Technology Stack

- **Infrastructure**: Terraform, AWS Lambda, CloudWatch
- **Backend**: Python 3.11
- **Frontend**: HTML5, CSS3, JavaScript (embedded)
- **AI/ML**: Pattern matching algorithm (educational demo)
- **Deployment**: Infrastructure as Code (IaC)

## 🎯 Use Cases

### Educational
- Learning AWS Lambda deployment
- Understanding serverless architecture
- Practicing Infrastructure as Code
- Exploring medical AI concepts

### Development
- Prototyping medical applications
- Testing AWS services integration
- Building proof-of-concepts
- API development practice

## 🤝 Contributing

This is an educational project. To enhance it:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided for educational purposes.

## 🆘 Support

### AWS Resources
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Free Tier](https://aws.amazon.com/free/)

### Terraform Resources
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform AWS Examples](https://github.com/hashicorp/terraform-provider-aws/tree/main/examples)

## ⚡ Next Steps

After successful deployment:

1. **Test the Application**: Open the Lambda function URL
2. **Review Logs**: Check CloudWatch for execution logs
3. **Monitor Costs**: Set up AWS Billing Alerts
4. **Explore Code**: Review `medical_diagnosis_lambda.py`
5. **Customize**: Add more diseases or modify treatments
6. **Secure**: Implement production security measures

## 🎓 Learning Resources

- AWS Serverless Application Model (SAM)
- Amazon Bedrock for production AI
- DynamoDB for patient data storage
- Amazon Comprehend Medical for NLP
- API Gateway for advanced routing

---

**Built with ❤️ for AWS and AI enthusiasts**

*Last Updated: January 2025*
