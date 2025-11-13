# 🚀 Terraform Deployment Guide - AI Medical Diagnosis System

Complete Infrastructure as Code (IaC) deployment guide for the AI Medical Diagnosis System using Terraform.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Verification](#verification)
- [Management](#management)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)
- [Best Practices](#best-practices)

---

## 🎯 Overview

### What is Terraform?

Terraform is an Infrastructure as Code (IaC) tool that allows you to define and deploy cloud resources using declarative configuration files. Benefits include:

- **Version Control**: Track infrastructure changes in Git
- **Reproducibility**: Deploy identical environments consistently
- **Automation**: Eliminate manual configuration steps
- **Documentation**: Infrastructure code serves as documentation
- **Safety**: Preview changes before applying them

### What Gets Deployed?

This Terraform configuration deploys:

1. **AWS Lambda Function** - The medical diagnosis application
2. **IAM Role & Policies** - Permissions for Lambda execution
3. **Function URL** - Public HTTPS endpoint (no API Gateway needed)
4. **CloudWatch Log Group** - For monitoring and debugging
5. **Optional Alarms** - CloudWatch alarms for errors, duration, throttles

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Terraform (IaC)                          │
│  - main.tf (resources)                                       │
│  - variables.tf (inputs)                                     │
│  - outputs.tf (results)                                      │
│  - versions.tf (providers)                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ terraform apply
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                               │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  Lambda        │  │  IAM Role      │  │  CloudWatch   │ │
│  │  Function      │←─│  & Policies    │→─│  Log Group    │ │
│  └───────┬────────┘  └────────────────┘  └───────────────┘ │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                         │
│  │  Function URL  │ (Public HTTPS Endpoint)                 │
│  └───────┬────────┘                                         │
└──────────┼──────────────────────────────────────────────────┘
           │
           ▼
     User's Browser
```

---

## 📦 Prerequisites

### 1. Install Terraform

**macOS (using Homebrew):**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux (Ubuntu/Debian):**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Windows (using Chocolatey):**
```powershell
choco install terraform
```

**Verify Installation:**
```bash
terraform version
# Should show: Terraform v1.x.x
```

### 2. Install AWS CLI

**macOS:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows:**
Download from: https://aws.amazon.com/cli/

**Verify Installation:**
```bash
aws --version
# Should show: aws-cli/2.x.x
```

### 3. Configure AWS Credentials

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your secret key
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

**Verify Configuration:**
```bash
aws sts get-caller-identity
# Should show your AWS Account ID, User ID, and ARN
```

### 4. Required AWS Permissions

Your AWS user/role needs these permissions:
- `lambda:*` - Create and manage Lambda functions
- `iam:CreateRole`, `iam:AttachRolePolicy` - Create IAM roles
- `logs:*` - Create CloudWatch log groups
- `cloudwatch:*` - Create alarms (optional)

---

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/jino-varghese/ai-execution.git
cd ai-execution
```

### 2. Navigate to Terraform Directory
```bash
cd terraform
```

### 3. Initialize Terraform
```bash
terraform init
```

This command:
- Downloads required providers (AWS, Archive)
- Initializes the backend
- Prepares the working directory

### 4. Preview Changes
```bash
terraform plan
```

This shows what will be created without making any changes.

### 5. Deploy Infrastructure
```bash
terraform apply
```

Type `yes` when prompted.

### 6. Get Your Application URL
```bash
terraform output function_url
```

**Open this URL in your browser!**

---

## 🔧 Detailed Setup

### Step 1: Initialize Terraform

```bash
cd terraform
terraform init
```

**What happens:**
- Downloads AWS provider (~100 MB)
- Downloads Archive provider (for ZIP files)
- Creates `.terraform` directory
- Creates `.terraform.lock.hcl` file

**Expected output:**
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Finding hashicorp/archive versions matching "~> 2.4"...
- Installing hashicorp/aws v5.x.x...
- Installing hashicorp/archive v2.4.x...

Terraform has been successfully initialized!
```

### Step 2: Configure Variables (Optional)

Create a `terraform.tfvars` file:

```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # or vim, code, etc.
```

**Customize values:**
```hcl
aws_region     = "us-east-1"
function_name  = "my-medical-diagnosis"
environment    = "dev"
memory_size    = 512
timeout        = 30
enable_alarms  = false
```

### Step 3: Validate Configuration

```bash
terraform validate
```

**Expected output:**
```
Success! The configuration is valid.
```

### Step 4: Plan Deployment

```bash
terraform plan -out=tfplan
```

**What this does:**
- Shows all resources to be created
- Calculates dependencies
- Saves plan to `tfplan` file

**Review the output:**
```
Terraform will perform the following actions:

  # aws_cloudwatch_log_group.lambda_log_group will be created
  + resource "aws_cloudwatch_log_group" "lambda_log_group" {
      + name              = "/aws/lambda/ai-medical-diagnosis"
      + retention_in_days = 7
      ...
    }

  # aws_iam_role.lambda_execution_role will be created
  + resource "aws_iam_role" "lambda_execution_role" {
      + name = "ai-medical-diagnosis-role"
      ...
    }

  # aws_lambda_function.medical_diagnosis will be created
  + resource "aws_lambda_function" "medical_diagnosis" {
      + function_name = "ai-medical-diagnosis"
      + memory_size   = 512
      + timeout       = 30
      ...
    }

Plan: 6 to add, 0 to change, 0 to destroy.
```

### Step 5: Apply Configuration

```bash
terraform apply tfplan
```

**Or apply without saved plan:**
```bash
terraform apply
```

Type `yes` when prompted.

**Deployment takes about 1-2 minutes.**

### Step 6: View Outputs

```bash
terraform output
```

**Expected output:**
```
deployment_success_message = <<EOT

  ╔════════════════════════════════════════════════════════════════╗
  ║          🎉 DEPLOYMENT SUCCESSFUL! 🎉                         ║
  ╚════════════════════════════════════════════════════════════════╝

  Your AI Medical Diagnosis System is now live!

  📍 Access your application at:
  https://abc123xyz.lambda-url.us-east-1.on.aws/

  ...
EOT

function_url = "https://abc123xyz.lambda-url.us-east-1.on.aws/"
function_name = "ai-medical-diagnosis"
aws_region = "us-east-1"
```

---

## ⚙️ Configuration

### Understanding Variables

All configurable options are in `variables.tf`. You can override defaults in three ways:

#### 1. Using terraform.tfvars File
```hcl
# terraform.tfvars
function_name = "my-custom-name"
memory_size   = 1024
```

#### 2. Using Command Line Flags
```bash
terraform apply -var="function_name=my-function" -var="memory_size=1024"
```

#### 3. Using Environment Variables
```bash
export TF_VAR_function_name="my-function"
export TF_VAR_memory_size=1024
terraform apply
```

### Key Configuration Options

#### Lambda Function Settings

```hcl
# Function name (must be unique in your AWS account)
function_name = "ai-medical-diagnosis"

# Python runtime version
python_runtime = "python3.11"  # Options: python3.9, python3.10, python3.11, python3.12

# Memory allocation (affects CPU power too)
memory_size = 512  # Range: 128-10240 MB

# Maximum execution time
timeout = 30  # Range: 1-900 seconds
```

#### Logging Settings

```hcl
# How long to keep logs
log_retention_days = 7  # Options: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, etc.

# Application log level
log_level = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### Monitoring Settings

```hcl
# Enable CloudWatch alarms
enable_alarms = true  # Set to true to enable monitoring alarms

# Enable X-Ray tracing for debugging
enable_xray_tracing = false
```

#### CORS Configuration

```hcl
# Allowed origins (use specific domains in production)
cors_allowed_origins = ["*"]  # For demo: ["*"], For prod: ["https://yourdomain.com"]

# Allowed HTTP methods
cors_allowed_methods = ["GET", "POST", "OPTIONS"]

# Allowed headers
cors_allowed_headers = ["content-type", "x-amz-date", "authorization"]

# CORS cache duration
cors_max_age = 86400  # 24 hours in seconds
```

#### Tags

```hcl
common_tags = {
  Project     = "AI-Medical-Diagnosis"
  ManagedBy   = "Terraform"
  Environment = "Development"
  Owner       = "Healthcare-AI-Team"
  CostCenter  = "Research"
}
```

---

## 🚀 Deployment

### Standard Deployment

```bash
# 1. Initialize
terraform init

# 2. Format code (optional but recommended)
terraform fmt

# 3. Validate
terraform validate

# 4. Plan
terraform plan

# 5. Apply
terraform apply
```

### Quick Deploy (One Command)

```bash
terraform init && terraform apply -auto-approve
```

**⚠️ Warning:** `-auto-approve` skips confirmation. Use carefully!

### Deploy to Different Environments

**Development:**
```bash
terraform apply -var="environment=dev" -var="enable_alarms=false"
```

**Staging:**
```bash
terraform apply -var="environment=staging" -var="enable_alarms=true" -var="memory_size=1024"
```

**Production:**
```bash
terraform apply -var="environment=prod" -var="enable_alarms=true" -var="memory_size=2048" -var="log_retention_days=30"
```

### Deploy with Specific Configuration File

```bash
terraform apply -var-file="production.tfvars"
```

---

## ✅ Verification

### 1. Check Deployment Status

```bash
terraform show
```

### 2. Test the Function URL

```bash
# Get the URL
FUNCTION_URL=$(terraform output -raw function_url)

# Test with curl
curl $FUNCTION_URL

# Should return HTML page
```

### 3. View CloudWatch Logs

```bash
# Get log command
terraform output view_logs_command

# Or directly
aws logs tail /aws/lambda/ai-medical-diagnosis --follow
```

### 4. Test Lambda Function Directly

```bash
# Invoke function
aws lambda invoke \
  --function-name ai-medical-diagnosis \
  --payload '{"requestContext":{"http":{"method":"GET"}}}' \
  response.json

# View response
cat response.json
```

### 5. Check All Resources

```bash
terraform state list
```

**Expected output:**
```
aws_cloudwatch_log_group.lambda_log_group
aws_iam_role.lambda_execution_role
aws_iam_role_policy_attachment.lambda_basic_execution
aws_lambda_function.medical_diagnosis
aws_lambda_function_url.medical_diagnosis_url
aws_lambda_permission.allow_function_url
data.archive_file.lambda_zip
data.aws_caller_identity.current
data.aws_region.current
```

---

## 🔄 Management

### Update Function Code

```bash
# Make changes to medical_diagnosis_lambda.py
# Then apply changes
terraform apply
```

Terraform automatically detects code changes and updates the function.

### Update Configuration

```bash
# Edit terraform.tfvars
nano terraform.tfvars

# Apply changes
terraform apply
```

### View Current State

```bash
# Show all resources
terraform state show

# Show specific resource
terraform state show aws_lambda_function.medical_diagnosis
```

### Refresh State

```bash
# Sync Terraform state with actual AWS resources
terraform refresh
```

### Import Existing Resources

If you have manually created resources:

```bash
terraform import aws_lambda_function.medical_diagnosis ai-medical-diagnosis
```

### Taint Resource (Force Recreate)

```bash
# Mark resource for recreation
terraform taint aws_lambda_function.medical_diagnosis

# Apply to recreate
terraform apply
```

---

## 🧹 Cleanup

### Destroy All Resources

```bash
terraform destroy
```

Type `yes` when prompted.

### Destroy Specific Resource

```bash
terraform destroy -target=aws_lambda_function.medical_diagnosis
```

### Preview Destruction

```bash
terraform plan -destroy
```

### Auto-Approve Destruction (Dangerous!)

```bash
terraform destroy -auto-approve
```

**⚠️ Use with extreme caution!**

---

## 🐛 Troubleshooting

### Issue: Terraform Init Fails

**Error:**
```
Error: Failed to query available provider packages
```

**Solution:**
```bash
# Clear cache and reinitialize
rm -rf .terraform .terraform.lock.hcl
terraform init
```

### Issue: AWS Credentials Not Found

**Error:**
```
Error: No valid credential sources found
```

**Solution:**
```bash
# Reconfigure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Issue: IAM Permission Denied

**Error:**
```
Error: creating IAM Role: AccessDenied
```

**Solution:**
- Ensure your AWS user has IAM permissions
- Contact AWS administrator to grant required permissions

### Issue: Lambda Function Already Exists

**Error:**
```
Error: creating Lambda Function: ResourceConflictException
```

**Solution:**
```bash
# Import existing function
terraform import aws_lambda_function.medical_diagnosis ai-medical-diagnosis

# Or change function name in variables
```

### Issue: State Lock Error

**Error:**
```
Error: Error acquiring the state lock
```

**Solution:**
```bash
# Force unlock (if no other operations running)
terraform force-unlock <LOCK_ID>
```

### Issue: ZIP File Not Found

**Error:**
```
Error: error archiving file: open ../medical_diagnosis_lambda.py: no such file or directory
```

**Solution:**
```bash
# Ensure you're in terraform directory
cd terraform

# Verify Lambda file exists
ls -la ../medical_diagnosis_lambda.py
```

### Debugging Tips

```bash
# Enable detailed logging
export TF_LOG=DEBUG
terraform apply

# Disable logging
unset TF_LOG

# Validate configuration
terraform validate

# Check syntax
terraform fmt -check

# View execution plan in detail
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan | jq
```

---

## 💰 Cost Optimization

### Free Tier Usage

AWS Lambda Free Tier includes:
- **1 million requests** per month FREE
- **400,000 GB-seconds** compute time FREE

**Your monthly cost: $0.00 - $0.50**

### Configuration for Minimal Cost

```hcl
# terraform.tfvars
memory_size    = 128  # Minimum memory
timeout        = 10   # Shorter timeout
enable_alarms  = false # Disable alarms
log_retention_days = 1 # Short log retention
```

### Prevent Runaway Costs

```hcl
# Set maximum concurrent executions
reserved_concurrent_executions = 10
```

### Monitor Costs

```bash
# View Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ai-medical-diagnosis \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

---

## 🏆 Best Practices

### 1. Version Control

```bash
# Commit Terraform files to Git
git add terraform/
git commit -m "Add Terraform infrastructure configuration"
git push
```

**Files to commit:**
- ✅ `main.tf`
- ✅ `variables.tf`
- ✅ `outputs.tf`
- ✅ `versions.tf`
- ✅ `.gitignore`
- ✅ `terraform.tfvars.example`

**Files to NEVER commit:**
- ❌ `terraform.tfvars` (contains secrets)
- ❌ `*.tfstate` (contains state)
- ❌ `.terraform/` (provider cache)

### 2. Remote State Backend

For team collaboration, use remote state:

```hcl
# versions.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "medical-diagnosis/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### 3. Use Workspaces

```bash
# Create workspace for each environment
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch workspace
terraform workspace select dev

# List workspaces
terraform workspace list
```

### 4. State Management

```bash
# Backup state before major changes
cp terraform.tfstate terraform.tfstate.backup

# List resources in state
terraform state list

# Remove resource from state (doesn't delete resource)
terraform state rm aws_lambda_function.medical_diagnosis
```

### 5. Security

```bash
# Scan for security issues
terraform plan | tfsec

# Check for misconfigurations
checkov -d terraform/

# Use AWS Secrets Manager for sensitive data
```

### 6. Documentation

Always document:
- Configuration variables
- Deployment steps
- Architecture decisions
- Change history

---

## 📚 Additional Resources

### Official Documentation
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

### Useful Commands Reference

```bash
# Initialize
terraform init

# Format code
terraform fmt -recursive

# Validate
terraform validate

# Plan
terraform plan

# Apply
terraform apply

# Destroy
terraform destroy

# Show state
terraform show

# List resources
terraform state list

# View outputs
terraform output

# Get specific output
terraform output function_url

# Refresh state
terraform refresh

# Import resource
terraform import <resource_type>.<name> <id>

# Remove resource from state
terraform state rm <resource_address>

# Move resource in state
terraform state mv <source> <destination>

# Taint resource
terraform taint <resource_address>

# Untaint resource
terraform untaint <resource_address>
```

---

## 🎉 Conclusion

You now have a professional, production-ready Terraform configuration for deploying the AI Medical Diagnosis System!

### What You've Learned:
- ✅ Infrastructure as Code with Terraform
- ✅ AWS Lambda deployment automation
- ✅ State management and versioning
- ✅ Configuration management
- ✅ Cost optimization strategies
- ✅ Security best practices

### Next Steps:
1. Deploy to multiple environments
2. Set up CI/CD pipeline
3. Add DynamoDB for data persistence
4. Integrate with Amazon Bedrock
5. Implement monitoring and alerting

---

**Happy Infrastructure Coding! 🚀**

*Last Updated: November 2025*
*Version: 1.0.0*
