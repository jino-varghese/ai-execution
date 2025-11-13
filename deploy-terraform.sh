#!/bin/bash

###############################################################################
# AWS Gen AI Dashboard - Terraform Deployment Script
# This script automates the deployment of the Lambda function using Terraform
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Main deployment function
main() {
    print_header "AWS Gen AI Dashboard - Terraform Deployment"

    # Check if Terraform is installed
    print_info "Checking Terraform installation..."
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        echo "Visit: https://www.terraform.io/downloads"
        exit 1
    fi
    print_success "Terraform is installed: $(terraform version | head -n 1)"

    # Check if AWS CLI is configured
    print_info "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    print_success "AWS CLI is configured"

    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        print_warning "terraform.tfvars not found."

        # Ask for OpenWeatherMap API key
        echo ""
        read -p "Enter your OpenWeatherMap API key (or press Enter to skip): " api_key

        if [ -z "$api_key" ]; then
            print_warning "Using default placeholder API key. Weather data may not work."
            api_key="YOUR_API_KEY_HERE"
        fi

        # Create terraform.tfvars from example
        print_info "Creating terraform.tfvars from template..."
        cp terraform.tfvars.example terraform.tfvars

        # Update API key in terraform.tfvars
        if [ "$(uname)" == "Darwin" ]; then
            # macOS
            sed -i '' "s/YOUR_API_KEY_HERE/$api_key/g" terraform.tfvars
        else
            # Linux
            sed -i "s/YOUR_API_KEY_HERE/$api_key/g" terraform.tfvars
        fi

        print_success "terraform.tfvars created"
    fi

    # Check if Python and pip are available
    print_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    print_success "Python is installed: $(python3 --version)"

    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi

    # Initialize Terraform
    print_header "Step 1: Initialize Terraform"
    terraform init
    print_success "Terraform initialized"

    # Validate Terraform configuration
    print_header "Step 2: Validate Configuration"
    terraform validate
    print_success "Configuration is valid"

    # Plan deployment
    print_header "Step 3: Plan Deployment"
    terraform plan -out=tfplan
    print_success "Deployment plan created"

    # Ask for confirmation
    echo ""
    read -p "Do you want to apply this plan? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_warning "Deployment cancelled by user."
        rm -f tfplan
        exit 0
    fi

    # Apply deployment
    print_header "Step 4: Apply Deployment"
    terraform apply tfplan
    rm -f tfplan

    print_success "Deployment completed successfully!"

    # Display outputs
    print_header "Deployment Information"
    terraform output

    echo ""
    print_success "Your Lambda Function URL is ready!"
    echo ""
    echo "Open the Function URL in your browser to access the dashboard."
    echo ""

    # Get the function URL
    function_url=$(terraform output -raw function_url 2>/dev/null || echo "Check 'terraform output' for the URL")
    echo "Function URL: $function_url"
    echo ""

    print_info "To view logs, run:"
    echo "  aws logs tail /aws/lambda/gen-ai-dashboard --follow"
    echo ""

    print_info "To destroy resources later, run:"
    echo "  terraform destroy"
    echo ""
}

# Run main function
main
