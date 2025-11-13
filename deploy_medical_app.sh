#!/bin/bash

# ============================================================================
# AI Medical Diagnosis System - AWS Deployment Script
# ============================================================================
# This script automates the deployment of the medical diagnosis application
# to AWS Lambda with a public Function URL.
#
# Prerequisites:
# - AWS CLI configured with valid credentials
# - Appropriate IAM permissions for Lambda, IAM role creation
#
# Usage:
#   chmod +x deploy_medical_app.sh
#   ./deploy_medical_app.sh
# ============================================================================

set -e  # Exit on any error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration variables
FUNCTION_NAME="ai-medical-diagnosis"
ROLE_NAME="ai-medical-diagnosis-role"
REGION="us-east-1"
PYTHON_VERSION="python3.11"
MEMORY_SIZE=512
TIMEOUT=30

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AI Medical Diagnosis System - AWS Deployment Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Verify AWS CLI is configured
# ============================================================================
echo -e "${YELLOW}[1/7] Verifying AWS CLI configuration...${NC}"

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not configured properly.${NC}"
    echo "Please run: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account ID: ${ACCOUNT_ID}${NC}"
echo ""

# ============================================================================
# Step 2: Create IAM Role for Lambda (if it doesn't exist)
# ============================================================================
echo -e "${YELLOW}[2/7] Creating IAM role for Lambda function...${NC}"

# Check if role already exists
if aws iam get-role --role-name ${ROLE_NAME} &> /dev/null; then
    echo -e "${GREEN}✅ Role ${ROLE_NAME} already exists${NC}"
else
    # Create trust policy for Lambda
    cat > /tmp/trust-policy.json << EOF
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

    # Create the IAM role
    aws iam create-role \
        --role-name ${ROLE_NAME} \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Execution role for AI Medical Diagnosis Lambda function" \
        > /dev/null

    # Attach basic Lambda execution policy (for CloudWatch Logs)
    aws iam attach-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    echo -e "${GREEN}✅ IAM role created: ${ROLE_NAME}${NC}"

    # Wait for role to be available
    echo "⏳ Waiting for IAM role to propagate (10 seconds)..."
    sleep 10
fi

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo ""

# ============================================================================
# Step 3: Package the Lambda function
# ============================================================================
echo -e "${YELLOW}[3/7] Packaging Lambda function...${NC}"

# Create a temporary directory for packaging
PACKAGE_DIR=$(mktemp -d)
echo "📦 Package directory: ${PACKAGE_DIR}"

# Copy the Lambda function
cp medical_diagnosis_lambda.py ${PACKAGE_DIR}/lambda_function.py

# Create ZIP file
cd ${PACKAGE_DIR}
zip -q function.zip lambda_function.py

echo -e "${GREEN}✅ Lambda function packaged successfully${NC}"
echo ""

# ============================================================================
# Step 4: Create or Update Lambda Function
# ============================================================================
echo -e "${YELLOW}[4/7] Deploying Lambda function...${NC}"

# Check if function already exists
if aws lambda get-function --function-name ${FUNCTION_NAME} --region ${REGION} &> /dev/null; then
    echo "🔄 Function exists, updating code..."

    # Update function code
    aws lambda update-function-code \
        --function-name ${FUNCTION_NAME} \
        --zip-file fileb://function.zip \
        --region ${REGION} \
        > /dev/null

    echo -e "${GREEN}✅ Lambda function code updated${NC}"

    # Update function configuration
    aws lambda update-function-configuration \
        --function-name ${FUNCTION_NAME} \
        --timeout ${TIMEOUT} \
        --memory-size ${MEMORY_SIZE} \
        --region ${REGION} \
        > /dev/null

    echo -e "${GREEN}✅ Lambda function configuration updated${NC}"

else
    echo "🆕 Creating new Lambda function..."

    # Create new function
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --runtime ${PYTHON_VERSION} \
        --role ${ROLE_ARN} \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://function.zip \
        --timeout ${TIMEOUT} \
        --memory-size ${MEMORY_SIZE} \
        --region ${REGION} \
        --description "AI-Powered Medical Diagnosis and Treatment Recommendations System" \
        > /dev/null

    echo -e "${GREEN}✅ Lambda function created${NC}"
fi

# Wait for function to be ready
echo "⏳ Waiting for function to be ready..."
aws lambda wait function-updated --function-name ${FUNCTION_NAME} --region ${REGION}

echo ""

# ============================================================================
# Step 5: Create Function URL (Public Endpoint)
# ============================================================================
echo -e "${YELLOW}[5/7] Creating public Function URL...${NC}"

# Check if Function URL already exists
if aws lambda get-function-url-config --function-name ${FUNCTION_NAME} --region ${REGION} &> /dev/null; then
    FUNCTION_URL=$(aws lambda get-function-url-config \
        --function-name ${FUNCTION_NAME} \
        --region ${REGION} \
        --query FunctionUrl \
        --output text)

    echo -e "${GREEN}✅ Function URL already exists${NC}"
else
    # Create Function URL with public access
    FUNCTION_URL=$(aws lambda create-function-url-config \
        --function-name ${FUNCTION_NAME} \
        --auth-type NONE \
        --cors '{
            "AllowOrigins": ["*"],
            "AllowMethods": ["GET", "POST", "OPTIONS"],
            "AllowHeaders": ["content-type"],
            "MaxAge": 86400
        }' \
        --region ${REGION} \
        --query FunctionUrl \
        --output text)

    echo -e "${GREEN}✅ Function URL created${NC}"
fi

echo ""

# ============================================================================
# Step 6: Add Public Access Permission
# ============================================================================
echo -e "${YELLOW}[6/7] Configuring public access permissions...${NC}"

# Add permission for public invocation
aws lambda add-permission \
    --function-name ${FUNCTION_NAME} \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region ${REGION} \
    &> /dev/null || echo "Permission already exists"

echo -e "${GREEN}✅ Public access configured${NC}"
echo ""

# ============================================================================
# Step 7: Cleanup and Display Results
# ============================================================================
echo -e "${YELLOW}[7/7] Cleaning up...${NC}"

# Clean up temporary files
cd - > /dev/null
rm -rf ${PACKAGE_DIR}
rm -f /tmp/trust-policy.json

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# ============================================================================
# Display Success Message and Access Information
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  🎉 DEPLOYMENT SUCCESSFUL! 🎉                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Your AI Medical Diagnosis System is now live!${NC}"
echo ""
echo -e "${BLUE}📍 Function URL:${NC}"
echo -e "${GREEN}${FUNCTION_URL}${NC}"
echo ""
echo -e "${BLUE}📊 Function Details:${NC}"
echo "  • Name:       ${FUNCTION_NAME}"
echo "  • Region:     ${REGION}"
echo "  • Runtime:    ${PYTHON_VERSION}"
echo "  • Memory:     ${MEMORY_SIZE} MB"
echo "  • Timeout:    ${TIMEOUT} seconds"
echo ""
echo -e "${BLUE}🔧 Next Steps:${NC}"
echo "  1. Open the Function URL in your browser"
echo "  2. Enter patient symptoms"
echo "  3. Get AI-powered diagnosis and treatment recommendations"
echo ""
echo -e "${BLUE}📚 Features:${NC}"
echo "  ✅ AI-powered symptom analysis"
echo "  ✅ Multiple diagnosis suggestions with confidence scores"
echo "  ✅ Treatment recommendations based on medical literature"
echo "  ✅ RAG-based research paper retrieval"
echo "  ✅ Emergency care indicators"
echo "  ✅ Responsive web interface"
echo ""
echo -e "${BLUE}📝 Monitoring:${NC}"
echo "  View logs:"
echo "  aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --region ${REGION}"
echo ""
echo -e "${BLUE}🧹 To Remove:${NC}"
echo "  Run: ./cleanup_medical_app.sh"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT DISCLAIMER:${NC}"
echo -e "${RED}This is an educational demo. NOT for actual medical use.${NC}"
echo -e "${RED}Always consult qualified healthcare professionals.${NC}"
echo ""
echo -e "${GREEN}Happy Learning! 🎓${NC}"
echo ""
