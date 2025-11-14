#!/bin/bash

################################################################################
# Test Script - Tests Lambda Function and Shows Exact Response
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FUNCTION_NAME="${1:-legal-document-analyzer}"
REGION="${2:-us-east-1}"

echo -e "${BLUE}Testing Lambda Function Response${NC}"
echo ""

# Get Function URL
echo "Getting Function URL..."
FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --query FunctionUrl \
    --output text 2>/dev/null)

if [ -z "$FUNCTION_URL" ]; then
    echo -e "${RED}No Function URL found!${NC}"
    exit 1
fi

echo -e "${GREEN}Function URL: $FUNCTION_URL${NC}"
echo ""

# Test with a simple document
TEST_DOC='This is a test Service Agreement. The Provider shall indemnify the Client for all claims. This agreement may be terminated with 30 days notice. The agreement is governed by the laws of California.'

echo "Sending POST request..."
echo ""

# Make request and save full response
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nCONTENT_TYPE:%{content_type}" "$FUNCTION_URL" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"document\":\"$TEST_DOC\",\"type\":\"contract\"}")

# Parse response
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
CONTENT_TYPE=$(echo "$RESPONSE" | grep "CONTENT_TYPE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d' | sed '/CONTENT_TYPE/d')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Response Details:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "HTTP Status: $HTTP_STATUS"
echo "Content-Type: $CONTENT_TYPE"
echo ""
echo "Body (first 500 characters):"
echo "----------------------------------------"
echo "$BODY" | head -c 500
echo ""
echo "----------------------------------------"
echo ""

# Check if it's JSON
if echo "$BODY" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Response is valid JSON${NC}"
    echo ""

    # Pretty print
    echo "Formatted JSON:"
    echo "$BODY" | python3 -m json.tool | head -50
    echo ""

    # Check for specific fields
    if echo "$BODY" | grep -q "risk_score"; then
        echo -e "${GREEN}✓ Contains 'risk_score' field${NC}"
        RISK_SCORE=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('risk_score', 'N/A'))")
        echo "  Risk Score: $RISK_SCORE"
    else
        echo -e "${YELLOW}⚠ Missing 'risk_score' field${NC}"
    fi

    if echo "$BODY" | grep -q "error"; then
        echo -e "${RED}✗ Response contains an error:${NC}"
        ERROR_MSG=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown'))")
        echo "  $ERROR_MSG"
    fi

else
    echo -e "${RED}✗ Response is NOT valid JSON${NC}"
    echo ""

    if echo "$BODY" | grep -q "<!DOCTYPE"; then
        echo -e "${RED}Response is HTML (this is the problem!)${NC}"
        echo ""
        echo "This means the Lambda function is returning HTML instead of JSON."
        echo "Common causes:"
        echo "  1. Lambda function has a syntax error"
        echo "  2. Lambda function is timing out"
        echo "  3. Lambda function is throwing an unhandled exception"
        echo "  4. Lambda Function URL configuration issue"
        echo ""
        echo "Next steps:"
        echo "  1. Check CloudWatch logs:"
        echo "     aws logs tail /aws/lambda/$FUNCTION_NAME --since 5m --region $REGION"
        echo ""
        echo "  2. Re-deploy the function:"
        echo "     ./update-lambda.sh"
        echo ""
        echo "  3. Check the deployed code hash to ensure it updated"
    else
        echo "Response appears to be plain text (not HTML or JSON)"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}CloudWatch Logs (last 20 lines):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws logs tail "/aws/lambda/$FUNCTION_NAME" \
    --since 5m \
    --region "$REGION" \
    --format short 2>/dev/null | tail -20 || echo "No recent logs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$HTTP_STATUS" = "200" ] && echo "$BODY" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Function is working correctly!${NC}"
else
    echo -e "${RED}✗ Function needs attention${NC}"
    echo ""
    echo "Run this to re-deploy:"
    echo "  ./update-lambda.sh"
fi

echo ""
