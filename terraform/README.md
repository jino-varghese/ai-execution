# Legal Document Analyzer - Terraform Deployment

Infrastructure as Code (IaC) for deploying the Legal Document Review and Contract Analysis Agent to AWS using Terraform.

## 📁 File Structure

```
terraform/
├── main.tf                      # Main infrastructure configuration
├── variables.tf                 # Input variable definitions
├── outputs.tf                   # Output value definitions
├── terraform.tfvars.example     # Example variable values
├── backend.tf.example           # Example remote state configuration
├── .gitignore                   # Git ignore rules for Terraform
└── README.md                    # This file
```

## 📋 Prerequisites

### 1. Install Terraform

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Windows:**
Download from: https://www.terraform.io/downloads

**Verify installation:**
```bash
terraform version
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or export credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3. Enable AWS Bedrock Access

1. Go to AWS Console → Amazon Bedrock
2. Click **Model access** → **Manage model access**
3. Enable **Anthropic Claude 3 Sonnet**
4. Submit and wait for approval (usually instant)

## 🚀 Quick Start Deployment

### Step 1: Prepare Configuration

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit variables (optional)
nano terraform.tfvars
```

### Step 2: Initialize Terraform

```bash
# Initialize Terraform (downloads providers)
terraform init
```

Expected output:
```
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

### Step 3: Plan Deployment

```bash
# Preview what will be created
terraform plan
```

This shows:
- IAM role and policies
- Lambda function
- Function URL
- CloudWatch log group
- Optional CloudWatch alarms

### Step 4: Deploy Infrastructure

```bash
# Apply the configuration
terraform apply

# Review the plan and type 'yes' to confirm
```

Expected output:
```
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.

Outputs:

function_url = "https://abc123xyz.lambda-url.us-east-1.on.aws/"
lambda_function_name = "legal-document-analyzer"
quick_start = <<EOT
==========================================
Legal Document Analysis Agent Deployed!
==========================================
...
```

### Step 5: Verify Deployment

```bash
# Open the Function URL in your browser
# URL is shown in terraform output

# Or retrieve it later
terraform output function_url
```

## 📝 Configuration Options

### Basic Configuration

Edit `terraform.tfvars`:

```hcl
# AWS Region
aws_region = "us-east-1"

# Environment
environment = "production"

# Lambda Configuration
lambda_function_name = "legal-doc-analyzer-prod"
lambda_memory_size   = 1024  # Increase for large documents
lambda_timeout       = 120   # Increase for complex analysis
```

### Advanced Configuration

#### Enable CloudWatch Alarms

```hcl
enable_cloudwatch_alarms = true
error_threshold          = 5
duration_threshold       = 50000
```

#### Configure Authentication

```hcl
# Require AWS IAM authentication
function_url_auth_type = "AWS_IAM"
```

#### Custom CORS Settings

```hcl
cors_allow_origins = ["https://yourdomain.com"]
cors_allow_methods = ["GET", "POST"]
cors_allow_headers = ["content-type"]
```

#### Environment Variables

```hcl
lambda_environment_variables = {
  LOG_LEVEL = "DEBUG"
  CUSTOM_VAR = "value"
}
```

## 🗂️ Resources Created

Terraform creates the following AWS resources:

| Resource | Type | Description |
|----------|------|-------------|
| IAM Role | `aws_iam_role` | Lambda execution role |
| IAM Policy Attachment | `aws_iam_role_policy_attachment` | Basic Lambda execution |
| IAM Inline Policy | `aws_iam_role_policy` | Bedrock access permissions |
| Lambda Function | `aws_lambda_function` | The legal analyzer function |
| Lambda Function URL | `aws_lambda_function_url` | Public HTTPS endpoint |
| Lambda Permission | `aws_lambda_permission` | Allow Function URL invocation |
| CloudWatch Log Group | `aws_cloudwatch_log_group` | Function logs |
| CloudWatch Alarms (optional) | `aws_cloudwatch_metric_alarm` | Monitoring alerts |

## 📊 Outputs

After deployment, Terraform provides useful outputs:

```bash
# View all outputs
terraform output

# View specific output
terraform output function_url

# View in JSON format
terraform output -json
```

Available outputs:
- `function_url` - The HTTPS endpoint to access the application
- `lambda_function_name` - Name of the deployed function
- `lambda_function_arn` - ARN of the Lambda function
- `cloudwatch_log_group_name` - CloudWatch log group name
- `deployment_info` - Complete deployment information
- `quick_start` - Quick start guide

## 🔄 Managing Infrastructure

### Update Configuration

```bash
# Modify terraform.tfvars or *.tf files
nano terraform.tfvars

# Preview changes
terraform plan

# Apply changes
terraform apply
```

### View Current State

```bash
# Show current infrastructure
terraform show

# List all resources
terraform state list

# Show specific resource
terraform state show aws_lambda_function.legal_analyzer
```

### Update Lambda Code

```bash
# After updating lambda_function.py
terraform apply -replace="aws_lambda_function.legal_analyzer"

# Or use taint (older Terraform versions)
terraform taint aws_lambda_function.legal_analyzer
terraform apply
```

### Destroy Infrastructure

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy

# Type 'yes' to confirm
```

## 🔐 Remote State Management (Recommended)

For team collaboration and state locking:

### 1. Create S3 Backend Resources

```bash
# Create S3 bucket for state
aws s3api create-bucket \
  --bucket my-terraform-state-bucket \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket my-terraform-state-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Configure Backend

```bash
# Copy example backend configuration
cp backend.tf.example backend.tf

# Edit with your bucket name
nano backend.tf
```

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "legal-document-analyzer/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### 3. Migrate State

```bash
# Initialize with new backend
terraform init -migrate-state
```

## 🐛 Troubleshooting

### Issue: "Error: creating Lambda Function"

**Cause:** IAM role not propagated yet

**Solution:**
```bash
# Wait 30 seconds and retry
sleep 30
terraform apply
```

### Issue: "AccessDeniedException" for Bedrock

**Cause:** Bedrock model access not enabled

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Enable Anthropic Claude 3 Sonnet
3. Wait for approval

### Issue: "InvalidParameterValueException" for Lambda

**Cause:** Invalid runtime or configuration

**Solution:**
```bash
# Verify variables
terraform plan

# Check supported runtimes
aws lambda list-runtimes
```

### Issue: Terraform State Lock

**Cause:** Previous operation didn't complete

**Solution:**
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID

# Get lock ID from error message
```

### Issue: Changes Outside Terraform

**Cause:** Resources modified via AWS Console

**Solution:**
```bash
# Import existing resources
terraform import aws_lambda_function.legal_analyzer function-name

# Or refresh state
terraform refresh
```

## 💰 Cost Estimation

Use Terraform to estimate costs:

```bash
# Install infracost
brew install infracost

# Register for free
infracost register

# Generate cost estimate
infracost breakdown --path .
```

**Estimated monthly costs:**
- Lambda: ~$0.20 (first 1M requests free)
- CloudWatch Logs: ~$0.50 (first 5GB free)
- Bedrock: ~$24/month (100 analyses)
- **Total: ~$25/month for 100 contract analyses**

## 📚 Terraform Best Practices

### 1. Use Variables

```hcl
# Don't hardcode values
# Bad
resource "aws_lambda_function" "example" {
  timeout = 60
}

# Good
resource "aws_lambda_function" "example" {
  timeout = var.lambda_timeout
}
```

### 2. Use Modules (for larger projects)

```hcl
module "legal_analyzer" {
  source = "./modules/lambda"

  function_name = "legal-doc-analyzer"
  memory_size   = 512
}
```

### 3. Enable State Locking

Always use remote backend with DynamoDB locking for team projects.

### 4. Use Workspaces for Environments

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Apply with workspace-specific vars
terraform apply -var-file="prod.tfvars"
```

### 5. Version Control

```bash
# Always commit terraform.lock.hcl
git add .terraform.lock.hcl

# Never commit sensitive files
# (already in .gitignore)
# - *.tfvars
# - *.tfstate
# - backend.tf (if contains secrets)
```

## 🔒 Security Considerations

### 1. Secure State Files

```hcl
# Enable encryption
backend "s3" {
  encrypt = true
}
```

### 2. Restrict Function URL

```hcl
# Use IAM authentication for production
function_url_auth_type = "AWS_IAM"
```

### 3. Enable CloudWatch Alarms

```hcl
enable_cloudwatch_alarms = true
```

### 4. Use Least Privilege IAM

The Terraform configuration already implements least privilege:
- Only necessary Bedrock permissions
- No wildcard (*) resources where possible
- CloudWatch logs permissions scoped to function

## 📖 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Terraform Guide](https://learn.hashicorp.com/tutorials/terraform/lambda-api-gateway)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

## 🆘 Support

### View Terraform Logs

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply

# Save to file
export TF_LOG_PATH=./terraform.log
```

### Common Commands Reference

```bash
# Format code
terraform fmt

# Validate configuration
terraform validate

# Show execution plan
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy

# Show outputs
terraform output

# View state
terraform show

# Refresh state
terraform refresh
```

---

**Terraform IaC for Legal Document Analysis Agent**

*Automated, Repeatable, Version-Controlled Infrastructure*
