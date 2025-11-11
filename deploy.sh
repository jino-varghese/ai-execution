#!/bin/bash

# AWS Lambda Gen AI Dashboard - Automated Deployment Script
# This script automates the deployment of the Lambda function

set -e  # Exit on error

echo "=================================="
echo "AWS Lambda Deployment Script"
echo "Gen AI Dashboard - Houston Weather"
echo "=================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
FUNCTION_NAME="gen-ai-dashboard"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
MEMORY_SIZE=256
TIMEOUT=30
REGION="us-east-1"  # Change this to your preferred region

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

echo -e "${BLUE}Step 1: Getting AWS Account Information${NC}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"
echo ""

# Ask for OpenWeatherMap API key
echo -e "${BLUE}Step 2: OpenWeatherMap API Key${NC}"
read -p "Enter your OpenWeatherMap API key (or press Enter to skip): " WEATHER_API_KEY
echo ""

# Check if IAM role exists, if not create it
echo -e "${BLUE}Step 3: Checking IAM Role${NC}"
ROLE_NAME="lambda-gen-ai-dashboard-role"
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
        --description "Execution role for Gen AI Dashboard Lambda"
    
    # Attach basic execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    echo "Waiting 10 seconds for IAM role to propagate..."
    sleep 10
fi
echo ""

# Create deployment package
echo -e "${BLUE}Step 4: Creating Deployment Package${NC}"
rm -rf package lambda-function.zip
mkdir -p package

# Install dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    #pip install -r requirements.txt -t package/ --quiet
fi

# Copy lambda function
cp lambda_function.py package/

# Create ZIP file
cd package
zip -r ../lambda-function.zip . > /dev/null
cd ..
echo "Deployment package created: lambda-function.zip"
echo ""

# Check if Lambda function exists
echo -e "${BLUE}Step 5: Deploying Lambda Function${NC}"
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-function.zip \
        --region $REGION > /dev/null
    
    echo "Function code updated successfully"
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
        --region $REGION > /dev/null
    
    echo "Function created successfully"
fi
echo ""

# Set environment variables if API key provided
if [ ! -z "$WEATHER_API_KEY" ]; then
    echo -e "${BLUE}Step 6: Setting Environment Variables${NC}"
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment Variables={OPENWEATHER_API_KEY=$WEATHER_API_KEY} \
        --region $REGION > /dev/null
    echo "Environment variables configured"
    echo ""
fi

# Create or update Function URL
echo -e "${BLUE}Step 7: Configuring Function URL${NC}"
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
fi
echo ""

# Clean up
echo -e "${BLUE}Step 8: Cleaning Up${NC}"
rm -rf package lambda-function.zip /tmp/trust-policy.json
echo "Temporary files removed"
echo ""

# Display results
echo -e "${GREEN}=================================="
echo "Deployment Complete!"
echo "==================================${NC}"
echo ""
echo -e "${GREEN}Your application is now live at:${NC}"
echo -e "${BLUE}$FUNCTION_URL${NC}"
echo ""
echo "Next Steps:"
echo "1. Open the URL in your browser"
echo "2. View the Houston weather and current time"
echo "3. Click on AWS Gen AI services to explore"
echo ""
echo "To view logs:"
echo "aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
echo ""
echo "To delete the function:"
echo "./cleanup.sh"
echo ""
