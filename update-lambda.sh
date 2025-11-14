#!/bin/bash

################################################################################
# Quick Lambda Update Script
# Updates Lambda function code with the fixed version
################################################################################

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

FUNCTION_NAME="${1:-legal-document-analyzer}"
REGION="${2:-us-east-1}"

echo -e "${BLUE}Quick Lambda Function Update${NC}"
echo "Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo ""

# Check if lambda_function.py exists
if [ ! -f "lambda_function.py" ]; then
    echo -e "${RED}Error: lambda_function.py not found!${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${BLUE}Step 1: Creating deployment package...${NC}"
zip -q lambda-function.zip lambda_function.py
echo -e "${GREEN}✓ Package created${NC}"

echo ""
echo -e "${BLUE}Step 2: Uploading to AWS Lambda...${NC}"

if aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file fileb://lambda-function.zip \
    --region "$REGION" > /dev/null 2>&1; then

    echo -e "${GREEN}✓ Function code updated successfully!${NC}"
else
    echo -e "${RED}✗ Failed to update function${NC}"
    echo ""
    echo "Possible reasons:"
    echo "  1. Function doesn't exist yet (use terraform/deploy.sh to create it)"
    echo "  2. AWS credentials not configured (run: aws configure)"
    echo "  3. Wrong function name or region"
    echo ""
    echo "To check if function exists:"
    echo "  aws lambda get-function --function-name $FUNCTION_NAME --region $REGION"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 3: Waiting for function to update...${NC}"
sleep 3
echo -e "${GREEN}✓ Update complete${NC}"

echo ""
echo -e "${BLUE}Step 4: Getting Function URL...${NC}"

FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name "$FUNCTION_NAME" \
    --region "$REGION" \
    --query FunctionUrl \
    --output text 2>/dev/null || echo "")

if [ -z "$FUNCTION_URL" ]; then
    echo -e "${YELLOW}⚠ No Function URL found${NC}"
    echo "Function exists but doesn't have a URL configured"
    echo ""
    echo "To create Function URL:"
    echo "  aws lambda create-function-url-config \\"
    echo "    --function-name $FUNCTION_NAME \\"
    echo "    --auth-type NONE \\"
    echo "    --cors AllowOrigins='*',AllowMethods='GET,POST,OPTIONS',AllowHeaders='content-type' \\"
    echo "    --region $REGION"
else
    echo -e "${GREEN}✓ Function URL: ${FUNCTION_URL}${NC}"
fi

echo ""
echo -e "${BLUE}Step 5: Testing the fix...${NC}"

if [ ! -z "$FUNCTION_URL" ]; then
    # Test POST request
    echo "Testing POST request..."

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$FUNCTION_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "document": "This is a test contract. The parties agree to indemnify each other. This agreement shall terminate upon 30 days notice.",
            "type": "contract"
        }' 2>&1)

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ POST request successful (HTTP 200)${NC}"

        # Check if response is valid JSON
        if echo "$BODY" | python3 -m json.tool > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Response is valid JSON${NC}"
            echo ""
            echo -e "${GREEN}${BOLD}FIX VERIFIED!${NC} The JSON error should be resolved."
        else
            echo -e "${RED}✗ Response is not valid JSON${NC}"
            echo "Response preview:"
            echo "$BODY" | head -c 200
        fi
    else
        echo -e "${YELLOW}⚠ HTTP Status: $HTTP_CODE${NC}"
        echo "Response preview:"
        echo "$BODY" | head -c 200
    fi
fi

# Cleanup
rm -f lambda-function.zip

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Update Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

if [ ! -z "$FUNCTION_URL" ]; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Open your browser"
    echo "  2. Go to: $FUNCTION_URL"
    echo "  3. Try analyzing a sample contract"
    echo ""
    echo "If you still see the error:"
    echo "  - Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
    echo "  - Check browser console for errors (F12)"
    echo "  - Wait 10 seconds and try again (Lambda cold start)"
fi

echo ""
