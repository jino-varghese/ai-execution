#!/bin/bash

################################################################################
# Lambda Function Debugging Script
# Helps diagnose issues with the deployed function
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

FUNCTION_NAME="${1:-legal-document-analyzer}"
REGION="${2:-us-east-1}"

echo -e "${BLUE}${BOLD}Lambda Function Diagnostics${NC}"
echo "Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI not installed${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Check if function exists
echo -e "${BLUE}Checking if function exists...${NC}"

if aws lambda get-function \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" &> /dev/null; then

    echo -e "${GREEN}✓ Function exists${NC}"

    # Get function details
    RUNTIME=$(aws lambda get-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --region "$REGION" \
        --query Runtime \
        --output text)

    MEMORY=$(aws lambda get-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --region "$REGION" \
        --query MemorySize \
        --output text)

    TIMEOUT=$(aws lambda get-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --region "$REGION" \
        --query Timeout \
        --output text)

    LAST_MODIFIED=$(aws lambda get-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --region "$REGION" \
        --query LastModified \
        --output text)

    echo "  Runtime: $RUNTIME"
    echo "  Memory: ${MEMORY}MB"
    echo "  Timeout: ${TIMEOUT}s"
    echo "  Last Modified: $LAST_MODIFIED"

else
    echo -e "${RED}✗ Function does not exist${NC}"
    echo ""
    echo "To create the function, run:"
    echo "  cd terraform"
    echo "  ./terraform-deploy.sh"
    exit 1
fi

echo ""

# Check Function URL
echo -e "${BLUE}Checking Function URL...${NC}"

FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --query FunctionUrl \
    --output text 2>/dev/null || echo "")

if [ -z "$FUNCTION_URL" ]; then
    echo -e "${RED}✗ No Function URL configured${NC}"
    echo ""
    echo "To create Function URL:"
    echo "  aws lambda create-function-url-config \\"
    echo "    --function-name $FUNCTION_NAME \\"
    echo "    --auth-type NONE \\"
    echo "    --cors AllowOrigins='*',AllowMethods='GET,POST,OPTIONS',AllowHeaders='content-type' \\"
    echo "    --region $REGION"
    exit 1
else
    echo -e "${GREEN}✓ Function URL exists${NC}"
    echo "  URL: $FUNCTION_URL"
fi

echo ""

# Test GET request
echo -e "${BLUE}Testing GET request (should return HTML)...${NC}"

GET_RESPONSE=$(curl -s -w "\n%{http_code}" "$FUNCTION_URL" 2>&1)
GET_HTTP_CODE=$(echo "$GET_RESPONSE" | tail -n 1)
GET_BODY=$(echo "$GET_RESPONSE" | head -n -1)

if [ "$GET_HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ GET request successful (HTTP 200)${NC}"

    if echo "$GET_BODY" | grep -q "<!DOCTYPE"; then
        echo -e "${GREEN}✓ Returns HTML (correct)${NC}"
    else
        echo -e "${YELLOW}⚠ Response doesn't look like HTML${NC}"
    fi
else
    echo -e "${RED}✗ GET request failed (HTTP $GET_HTTP_CODE)${NC}"
    echo "Response:"
    echo "$GET_BODY" | head -c 500
fi

echo ""

# Test POST request
echo -e "${BLUE}Testing POST request (should return JSON)...${NC}"

TEST_PAYLOAD='{
  "document": "EMPLOYMENT AGREEMENT\n\nThis Employment Agreement is made between Employer Inc. and Employee.\n\n1. POSITION\nEmployee is hired as Senior Software Engineer.\n\n2. COMPENSATION\nBase salary of $150,000 per year.\n\n3. TERMINATION\nEmployment is at-will and may be terminated by either party.",
  "type": "contract"
}'

POST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$FUNCTION_URL" \
    -H "Content-Type: application/json" \
    -d "$TEST_PAYLOAD" 2>&1)

POST_HTTP_CODE=$(echo "$POST_RESPONSE" | tail -n 1)
POST_BODY=$(echo "$POST_RESPONSE" | head -n -1)

echo "  HTTP Status: $POST_HTTP_CODE"

if [ "$POST_HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ POST request successful${NC}"

    # Check if JSON
    if echo "$POST_BODY" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Response is valid JSON${NC}"

        # Parse response
        if echo "$POST_BODY" | grep -q "risk_score"; then
            echo -e "${GREEN}✓ Contains expected fields (risk_score)${NC}"

            RISK_SCORE=$(echo "$POST_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('risk_score', 'N/A'))")
            RISK_LEVEL=$(echo "$POST_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('risk_level', 'N/A'))")

            echo ""
            echo "  Sample Analysis Results:"
            echo "    Risk Score: $RISK_SCORE"
            echo "    Risk Level: $RISK_LEVEL"
        else
            echo -e "${YELLOW}⚠ Missing expected fields${NC}"
        fi
    else
        echo -e "${RED}✗ Response is NOT valid JSON${NC}"
        echo ""
        echo "This is the problem! Response starts with:"
        echo "$POST_BODY" | head -c 200
        echo ""
        echo -e "${YELLOW}Solution: Run ./update-lambda.sh to deploy the fix${NC}"
    fi
else
    echo -e "${RED}✗ POST request failed (HTTP $POST_HTTP_CODE)${NC}"
    echo "Response:"
    echo "$POST_BODY" | head -c 500
fi

echo ""

# Check recent logs
echo -e "${BLUE}Checking recent logs...${NC}"

LOG_GROUP="/aws/lambda/$FUNCTION_NAME"

if aws logs describe-log-groups \
    --log-group-name-prefix "$LOG_GROUP" \
    --region "$REGION" &> /dev/null; then

    echo -e "${GREEN}✓ Log group exists${NC}"

    echo ""
    echo "Recent log entries (last 5 minutes):"
    echo "────────────────────────────────────────"

    aws logs tail "$LOG_GROUP" \
        --since 5m \
        --region "$REGION" \
        --format short 2>/dev/null | head -20 || echo "No recent logs"

else
    echo -e "${YELLOW}⚠ No log group found${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Diagnosis Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

if [ "$POST_HTTP_CODE" = "200" ] && echo "$POST_BODY" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}${BOLD}✓ Function is working correctly!${NC}"
    echo ""
    echo "The JSON error should be resolved."
    echo "If you still see issues in browser:"
    echo "  1. Clear browser cache (Ctrl+Shift+R)"
    echo "  2. Open browser console (F12) and check for errors"
    echo "  3. Try in an incognito/private window"
else
    echo -e "${RED}${BOLD}✗ Function needs to be updated${NC}"
    echo ""
    echo "To fix the JSON error, run:"
    echo -e "  ${YELLOW}./update-lambda.sh${NC}"
    echo ""
    echo "This will deploy the fixed version that returns proper JSON."
fi

echo ""
