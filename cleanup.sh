#!/bin/bash

# Cleanup Script - Removes all AWS resources created by the deployment

set -e

echo "=================================="
echo "AWS Lambda Cleanup Script"
echo "=================================="
echo ""

# Configuration
FUNCTION_NAME="gen-ai-dashboard"
ROLE_NAME="lambda-gen-ai-dashboard-role"
REGION="us-east-1"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}WARNING: This will delete the following resources:${NC}"
echo "- Lambda Function: $FUNCTION_NAME"
echo "- IAM Role: $ROLE_NAME"
echo "- Function URL configuration"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo -e "${RED}Starting cleanup...${NC}"
echo ""

# Delete Function URL
echo "Removing Function URL..."
aws lambda delete-function-url-config \
    --function-name $FUNCTION_NAME \
    --region $REGION 2>/dev/null || echo "Function URL not found or already deleted"

# Delete Lambda function
echo "Deleting Lambda function..."
aws lambda delete-function \
    --function-name $FUNCTION_NAME \
    --region $REGION 2>/dev/null || echo "Function not found or already deleted"

# Detach policies from role
echo "Detaching IAM policies..."
aws iam detach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true

# Delete IAM role
echo "Deleting IAM role..."
aws iam delete-role \
    --role-name $ROLE_NAME 2>/dev/null || echo "IAM role not found or already deleted"

echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
echo "All resources have been removed."
echo ""
