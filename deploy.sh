#!/bin/bash

# Legal Document Analysis Agent - Automated AWS Deployment Script
# This script automates the deployment of the Legal Document Review and Contract Analysis Agent

set -e  # Exit on error

echo "=========================================="
echo "Legal Document Analysis Agent"
echo "AWS Lambda Deployment Script"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FUNCTION_NAME="legal-document-analyzer"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
MEMORY_SIZE=512
TIMEOUT=60
REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Function Name: $FUNCTION_NAME"
echo "  Runtime: $RUNTIME"
echo "  Region: $REGION"
echo "  Memory: ${MEMORY_SIZE}MB"
echo "  Timeout: ${TIMEOUT}s"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Please run: aws configure"
    exit 1
fi

echo -e "${BLUE}Step 1: Verifying AWS Account${NC}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"
echo ""

# Check if IAM role exists, if not create it
echo -e "${BLUE}Step 2: Setting up IAM Role${NC}"
ROLE_NAME="legal-document-analyzer-role"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo "IAM Role already exists: $ROLE_NAME"
else
    echo "Creating IAM Role: $ROLE_NAME"

    # Create trust policy
    cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Execution role for Legal Document Analysis Agent"

    # Attach basic execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    # Create and attach Bedrock policy
    cat > /tmp/bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name BedrockAccess \
        --policy-document file:///tmp/bedrock-policy.json

    echo "Waiting 15 seconds for IAM role to propagate..."
    sleep 15
fi
echo ""

# Create deployment package
echo -e "${BLUE}Step 3: Creating Deployment Package${NC}"
rm -rf package lambda-function.zip

# Check if we need to install dependencies
if [ -f requirements.txt ] && [ -s requirements.txt ]; then
    echo "Installing Python dependencies..."
    mkdir -p package
    pip install -r requirements.txt -t package/ --quiet --upgrade

    # Copy lambda function
    cp lambda_function.py package/

    # Create ZIP file
    cd package
    zip -r ../lambda-function.zip . > /dev/null
    cd ..

    echo "Deployment package created with dependencies"
else
    # No dependencies, just package the function
    zip lambda-function.zip lambda_function.py > /dev/null
    echo "Deployment package created (no external dependencies)"
fi

PACKAGE_SIZE=$(du -h lambda-function.zip | cut -f1)
echo "Package size: $PACKAGE_SIZE"
echo ""

# Check if Lambda function exists
echo -e "${BLUE}Step 4: Deploying Lambda Function${NC}"
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-function.zip \
        --region $REGION > /dev/null

    # Update configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --region $REGION > /dev/null

    echo "Function updated successfully"
else
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda-function.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --region $REGION \
        --description "Legal Document Review and Contract Analysis Agent with AI-powered risk assessment" > /dev/null

    echo "Function created successfully"
fi
echo ""

# Create or update Function URL
echo -e "${BLUE}Step 5: Configuring Function URL${NC}"
if aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "Function URL already exists"
    FUNCTION_URL=$(aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION --query FunctionUrl --output text)
else
    echo "Creating Function URL..."
    FUNCTION_URL=$(aws lambda create-function-url-config \
        --function-name $FUNCTION_NAME \
        --auth-type NONE \
        --cors AllowOrigins="*",AllowMethods="GET,POST",AllowHeaders="content-type" \
        --region $REGION \
        --query FunctionUrl \
        --output text)

    # Add permission for public access
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id FunctionURLAllowPublicAccess \
        --action lambda:InvokeFunctionUrl \
        --principal "*" \
        --function-url-auth-type NONE \
        --region $REGION > /dev/null 2>&1 || true

    echo "Function URL created successfully"
fi
echo ""

# Clean up
echo -e "${BLUE}Step 6: Cleaning Up${NC}"
rm -rf package lambda-function.zip /tmp/trust-policy.json /tmp/bedrock-policy.json
echo "Temporary files removed"
echo ""

# Display results
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo -e "${GREEN}Legal Document Analysis Agent is live!${NC}"
echo ""
echo -e "${BLUE}Access URL:${NC}"
echo -e "${YELLOW}$FUNCTION_URL${NC}"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "  ✓ AI-Powered Contract Analysis (AWS Bedrock/Claude)"
echo "  ✓ Risk Assessment & Detection"
echo "  ✓ Legal Precedent Matching (RAG)"
echo "  ✓ Missing Clause Identification"
echo "  ✓ Actionable Recommendations"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Open the URL in your browser"
echo "  2. Paste a contract or legal document"
echo "  3. Click 'Analyze Document' to get AI-powered insights"
echo "  4. Try the sample contracts (NDA, Service Agreement, Employment)"
echo ""
echo -e "${BLUE}AWS Bedrock Setup (if not already done):${NC}"
echo "  1. Go to AWS Console > Bedrock > Model access"
echo "  2. Request access to 'Anthropic Claude 3 Sonnet'"
echo "  3. Wait for approval (usually instant)"
echo ""
echo -e "${BLUE}Monitor Logs:${NC}"
echo "  aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
echo ""
echo -e "${BLUE}Update Function:${NC}"
echo "  ./deploy.sh"
echo ""
echo -e "${BLUE}Delete Function:${NC}"
echo "  ./cleanup.sh"
echo ""
echo -e "${GREEN}Happy Analyzing! ⚖️${NC}"
echo ""
