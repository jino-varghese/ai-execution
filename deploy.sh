#!/bin/bash

# AI Travel Itinerary Generator - Deployment Script
# This script automates the Terraform deployment process

set -e  # Exit on error

echo "================================"
echo "AI Travel Itinerary Deployment"
echo "================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    echo "   Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first."
    echo "   Visit: https://www.terraform.io/downloads"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured."
    echo "   Run: aws configure"
    exit 1
fi

echo "✅ All prerequisites met"
echo ""

# Navigate to terraform directory
cd "$(dirname "$0")/terraform"

echo "Step 1: Initializing Terraform..."
terraform init

echo ""
echo "Step 2: Validating configuration..."
terraform validate

echo ""
echo "Step 3: Planning deployment..."
terraform plan -out=tfplan

echo ""
read -p "Do you want to proceed with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    rm -f tfplan
    exit 0
fi

echo ""
echo "Step 4: Applying Terraform configuration..."
terraform apply tfplan

rm -f tfplan

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Copy the API Gateway URL from the output above"
echo "2. Edit frontend/js/app.js and update CONFIG.API_ENDPOINT"
echo "3. Upload the updated file:"
echo ""

# Get bucket name from Terraform output
BUCKET_NAME=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "YOUR_BUCKET_NAME")
echo "   aws s3 cp ../frontend/js/app.js s3://$BUCKET_NAME/js/app.js"
echo ""

# Get website URL
WEBSITE_URL=$(terraform output -raw website_url 2>/dev/null || echo "Check Terraform outputs")
echo "4. Visit your website: $WEBSITE_URL"
echo ""
echo "================================"
