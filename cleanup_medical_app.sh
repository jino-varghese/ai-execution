#!/bin/bash

# ============================================================================
# AI Medical Diagnosis System - Cleanup Script
# ============================================================================
# This script removes all AWS resources created by the deployment script.
#
# Usage:
#   chmod +x cleanup_medical_app.sh
#   ./cleanup_medical_app.sh
# ============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
FUNCTION_NAME="ai-medical-diagnosis"
ROLE_NAME="ai-medical-diagnosis-role"
REGION="us-east-1"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      AI Medical Diagnosis System - Cleanup Script            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirmation prompt
echo -e "${YELLOW}⚠️  This will delete the following resources:${NC}"
echo "  • Lambda Function: ${FUNCTION_NAME}"
echo "  • IAM Role: ${ROLE_NAME}"
echo "  • Function URL configuration"
echo "  • CloudWatch Log Group"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}[1/4] Deleting Lambda Function URL...${NC}"
aws lambda delete-function-url-config \
    --function-name ${FUNCTION_NAME} \
    --region ${REGION} \
    &> /dev/null || echo "Function URL not found or already deleted"
echo -e "${GREEN}✅ Function URL deleted${NC}"
echo ""

echo -e "${YELLOW}[2/4] Deleting Lambda Function...${NC}"
aws lambda delete-function \
    --function-name ${FUNCTION_NAME} \
    --region ${REGION} \
    &> /dev/null || echo "Function not found or already deleted"
echo -e "${GREEN}✅ Lambda function deleted${NC}"
echo ""

echo -e "${YELLOW}[3/4] Deleting IAM Role...${NC}"
# Detach managed policies
aws iam detach-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    &> /dev/null || echo "Policy already detached"

# Delete the role
aws iam delete-role \
    --role-name ${ROLE_NAME} \
    &> /dev/null || echo "Role not found or already deleted"
echo -e "${GREEN}✅ IAM role deleted${NC}"
echo ""

echo -e "${YELLOW}[4/4] Deleting CloudWatch Log Group...${NC}"
aws logs delete-log-group \
    --log-group-name /aws/lambda/${FUNCTION_NAME} \
    --region ${REGION} \
    &> /dev/null || echo "Log group not found or already deleted"
echo -e "${GREEN}✅ CloudWatch logs deleted${NC}"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  🎉 CLEANUP COMPLETE! 🎉                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "All resources have been successfully removed."
echo ""
