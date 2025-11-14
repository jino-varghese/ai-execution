#!/bin/bash

# Legal Document Analysis Agent - Cleanup Script
# This script removes all AWS resources created by the deployment

set -e

echo "=========================================="
echo "Legal Document Analysis Agent"
echo "AWS Resource Cleanup Script"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FUNCTION_NAME="legal-document-analyzer"
ROLE_NAME="legal-document-analyzer-role"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${YELLOW}WARNING: This will delete the following resources:${NC}"
echo "  - Lambda function: $FUNCTION_NAME"
echo "  - IAM role: $ROLE_NAME"
echo "  - Function URL configuration"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# Delete Lambda function
echo "1. Deleting Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    aws lambda delete-function --function-name $FUNCTION_NAME --region $REGION
    echo -e "${GREEN}Lambda function deleted${NC}"
else
    echo "Lambda function not found (already deleted)"
fi

# Delete IAM role
echo "2. Deleting IAM role..."
if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    # Detach managed policies
    aws iam detach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole &> /dev/null || true

    # Delete inline policies
    aws iam delete-role-policy \
        --role-name $ROLE_NAME \
        --policy-name BedrockAccess &> /dev/null || true

    # Delete role
    aws iam delete-role --role-name $ROLE_NAME
    echo -e "${GREEN}IAM role deleted${NC}"
else
    echo "IAM role not found (already deleted)"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Cleanup Complete!"
echo "==========================================${NC}"
echo ""
echo "All AWS resources have been removed."
echo ""
