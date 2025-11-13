#!/bin/bash

################################################################################
# AI Medical Diagnosis System - AWS Deployment Script
################################################################################
# This script automates the deployment of the Medical Diagnosis System to AWS
# using Terraform.
#
# Usage: ./deploy.sh
################################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "============================================================"
    echo "  🏥 AI Medical Diagnosis System - AWS Deployment"
    echo "============================================================"
    echo ""
}

print_separator() {
    echo "------------------------------------------------------------"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local all_ok=true

    # Check AWS CLI
    if command_exists aws; then
        log_success "AWS CLI is installed ($(aws --version 2>&1 | cut -d' ' -f1))"
    else
        log_error "AWS CLI is not installed"
        log_info "Install from: https://aws.amazon.com/cli/"
        all_ok=false
    fi

    # Check Terraform
    if command_exists terraform; then
        log_success "Terraform is installed ($(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4))"
    else
        log_error "Terraform is not installed"
        log_info "Install from: https://developer.hashicorp.com/terraform/downloads"
        all_ok=false
    fi

    if [ "$all_ok" = false ]; then
        log_error "Prerequisites check failed. Please install missing tools."
        exit 1
    fi

    print_separator
}

# Check AWS credentials
check_aws_credentials() {
    log_info "Checking AWS credentials..."

    if aws sts get-caller-identity >/dev/null 2>&1; then
        local account_id=$(aws sts get-caller-identity --query Account --output text)
        local user_arn=$(aws sts get-caller-identity --query Arn --output text)
        log_success "AWS credentials are configured"
        log_info "Account ID: $account_id"
        log_info "User/Role: $user_arn"
    else
        log_error "AWS credentials are not configured or invalid"
        log_info "Run: aws configure"
        exit 1
    fi

    print_separator
}

# Setup Terraform variables
setup_terraform_vars() {
    log_info "Checking Terraform variables configuration..."

    if [ ! -f "terraform.tfvars" ]; then
        log_warning "terraform.tfvars not found. Creating from example..."
        if [ -f "terraform.tfvars.example" ]; then
            cp terraform.tfvars.example terraform.tfvars
            log_success "Created terraform.tfvars from example"
            log_warning "Please review and customize terraform.tfvars if needed"

            # Ask if user wants to edit
            read -p "$(echo -e ${YELLOW}Do you want to edit terraform.tfvars now? [y/N]:${NC} )" -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} terraform.tfvars
            fi
        else
            log_error "terraform.tfvars.example not found!"
            exit 1
        fi
    else
        log_success "terraform.tfvars found"
    fi

    print_separator
}

# Initialize Terraform
terraform_init() {
    log_info "Initializing Terraform..."

    if terraform init; then
        log_success "Terraform initialized successfully"
    else
        log_error "Terraform initialization failed"
        exit 1
    fi

    print_separator
}

# Validate Terraform configuration
terraform_validate() {
    log_info "Validating Terraform configuration..."

    if terraform validate; then
        log_success "Terraform configuration is valid"
    else
        log_error "Terraform configuration validation failed"
        exit 1
    fi

    print_separator
}

# Show Terraform plan
terraform_plan() {
    log_info "Generating Terraform execution plan..."
    echo ""

    if terraform plan -out=tfplan; then
        log_success "Terraform plan generated successfully"
    else
        log_error "Terraform plan failed"
        exit 1
    fi

    print_separator
}

# Apply Terraform
terraform_apply() {
    log_info "Deploying infrastructure to AWS..."
    echo ""

    # Confirm deployment
    read -p "$(echo -e ${YELLOW}Do you want to proceed with deployment? [y/N]:${NC} )" -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Deployment cancelled by user"
        rm -f tfplan
        exit 0
    fi

    if terraform apply tfplan; then
        log_success "Infrastructure deployed successfully!"
        rm -f tfplan
    else
        log_error "Terraform apply failed"
        rm -f tfplan
        exit 1
    fi

    print_separator
}

# Display outputs
show_outputs() {
    log_info "Deployment completed! Here are your outputs:"
    echo ""

    terraform output -json > /tmp/tf_output.json

    # Extract key outputs
    local lambda_url=$(terraform output -raw lambda_function_url 2>/dev/null || echo "N/A")
    local function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "N/A")
    local region=$(terraform output -raw deployment_region 2>/dev/null || echo "N/A")
    local log_group=$(terraform output -raw cloudwatch_log_group 2>/dev/null || echo "N/A")

    echo "============================================================"
    echo "  🎉 DEPLOYMENT SUCCESSFUL!"
    echo "============================================================"
    echo ""
    echo "📱 Application URL:"
    echo "   $lambda_url"
    echo ""
    echo "⚙️  Lambda Function:"
    echo "   Name: $function_name"
    echo "   Region: $region"
    echo ""
    echo "📊 CloudWatch Logs:"
    echo "   Log Group: $log_group"
    echo ""
    echo "🔗 AWS Console Links:"
    echo "   Lambda: https://console.aws.amazon.com/lambda/home?region=${region}#/functions/${function_name}"
    echo "   Logs: https://console.aws.amazon.com/cloudwatch/home?region=${region}#logsV2:log-groups"
    echo ""
    echo "💡 Next Steps:"
    echo "   1. Open the Application URL in your browser"
    echo "   2. Test the medical diagnosis system"
    echo "   3. Monitor logs in CloudWatch"
    echo ""
    echo "⚠️  REMINDER: This is an educational demo only."
    echo "    NOT for actual medical use."
    echo ""
    echo "============================================================"
    echo ""

    # Save outputs to file
    echo "$lambda_url" > .deployment_url
    log_success "Deployment URL saved to .deployment_url"

    rm -f /tmp/tf_output.json
}

# Estimate costs
show_cost_estimate() {
    log_info "💰 Estimated Monthly Cost:"
    echo ""
    echo "  Within AWS Free Tier:"
    echo "    - Lambda: \$0.00 (1M requests/month free)"
    echo "    - CloudWatch Logs: \$0.00 (5GB/month free)"
    echo "    - Data Transfer: \$0.00 (within free tier)"
    echo ""
    echo "  Total: \$0.00 - \$1.00/month"
    echo ""
    print_separator
}

# Main deployment flow
main() {
    print_banner

    # Change to script directory
    cd "$(dirname "$0")"

    # Run deployment steps
    check_prerequisites
    check_aws_credentials
    setup_terraform_vars
    show_cost_estimate
    terraform_init
    terraform_validate
    terraform_plan
    terraform_apply
    show_outputs

    log_success "Deployment completed successfully! 🎉"
    echo ""
}

# Trap errors
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"
