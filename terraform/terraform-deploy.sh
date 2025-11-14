#!/bin/bash

################################################################################
# Legal Document Analyzer - Terraform Deployment Script
#
# This script automates the complete deployment process:
# - Checks prerequisites
# - Sets up configuration
# - Initializes Terraform
# - Plans infrastructure changes
# - Deploys to AWS
# - Displays access information
################################################################################

set -e  # Exit on any error
set -o pipefail  # Exit on pipe failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${TERRAFORM_DIR}/deployment_${TIMESTAMP}.log"

# Deployment options
AUTO_APPROVE=false
SKIP_PLAN=false
VERBOSE=false

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║     Legal Document Analysis Agent - Terraform Deploy      ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo ""
    log "${MAGENTA}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${MAGENTA}${BOLD}Step $1: $2${NC}"
    log "${MAGENTA}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_separator() {
    log "${CYAN}────────────────────────────────────────────────────────────${NC}"
}

confirm() {
    if [ "$AUTO_APPROVE" = true ]; then
        return 0
    fi

    echo -e "${YELLOW}$1${NC}"
    read -p "Continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log_error "Deployment cancelled by user"
        exit 1
    fi
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    log_success "$1 is installed"
    return 0
}

################################################################################
# Prerequisite Checks
################################################################################

check_prerequisites() {
    print_step 1 "Checking Prerequisites"

    local prereqs_met=true

    # Check Terraform
    log_info "Checking for Terraform..."
    if check_command terraform; then
        local tf_version=$(terraform version -json | grep -o '"terraform_version":"[^"]*"' | cut -d'"' -f4)
        log_info "Terraform version: $tf_version"
    else
        prereqs_met=false
        log_error "Please install Terraform: https://www.terraform.io/downloads"
    fi

    # Check AWS CLI
    log_info "Checking for AWS CLI..."
    if check_command aws; then
        local aws_version=$(aws --version 2>&1 | cut -d' ' -f1)
        log_info "$aws_version"
    else
        prereqs_met=false
        log_error "Please install AWS CLI: https://aws.amazon.com/cli/"
    fi

    # Check AWS credentials
    if [ "$prereqs_met" = true ]; then
        log_info "Checking AWS credentials..."
        if aws sts get-caller-identity &> /dev/null; then
            local account_id=$(aws sts get-caller-identity --query Account --output text)
            local user_arn=$(aws sts get-caller-identity --query Arn --output text)
            log_success "AWS credentials configured"
            log_info "Account ID: $account_id"
            log_info "User: $user_arn"
        else
            prereqs_met=false
            log_error "AWS credentials not configured"
            log_error "Please run: aws configure"
        fi
    fi

    # Check for lambda_function.py
    log_info "Checking for Lambda function code..."
    if [ -f "${TERRAFORM_DIR}/../lambda_function.py" ]; then
        log_success "Lambda function code found"
    else
        prereqs_met=false
        log_error "lambda_function.py not found at ${TERRAFORM_DIR}/../lambda_function.py"
    fi

    if [ "$prereqs_met" = false ]; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    log_success "All prerequisites met"
}

################################################################################
# Configuration Setup
################################################################################

setup_configuration() {
    print_step 2 "Setting Up Configuration"

    cd "$TERRAFORM_DIR"

    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        log_warning "terraform.tfvars not found"

        if [ -f "terraform.tfvars.example" ]; then
            log_info "Creating terraform.tfvars from example..."
            cp terraform.tfvars.example terraform.tfvars
            log_success "Created terraform.tfvars"

            echo ""
            log_warning "Please review and customize terraform.tfvars before continuing"
            log_info "Key settings to review:"
            echo "  - aws_region (default: us-east-1)"
            echo "  - lambda_function_name"
            echo "  - lambda_memory_size"
            echo "  - function_url_auth_type (NONE for public, AWS_IAM for private)"
            echo ""

            if [ "$AUTO_APPROVE" = false ]; then
                read -p "Press Enter to continue with default values, or Ctrl+C to edit first..."
            fi
        else
            log_error "terraform.tfvars.example not found"
            exit 1
        fi
    else
        log_success "terraform.tfvars found"
    fi

    # Display current configuration
    log_info "Current configuration:"
    if [ -f "terraform.tfvars" ]; then
        grep -v '^#' terraform.tfvars | grep -v '^$' | head -10 | while read -r line; do
            log "  ${CYAN}$line${NC}"
        done
    fi
}

################################################################################
# Bedrock Access Check
################################################################################

check_bedrock_access() {
    print_step 3 "Checking AWS Bedrock Access"

    log_info "Verifying Bedrock model access..."

    local region=$(grep 'aws_region' terraform.tfvars | cut -d'"' -f2 || echo "us-east-1")

    if aws bedrock list-foundation-models --region "$region" &> /dev/null; then
        log_success "Bedrock API is accessible"

        # Check for Claude models
        if aws bedrock list-foundation-models --region "$region" 2>/dev/null | grep -i "claude" &> /dev/null; then
            log_success "Claude models are available"
        else
            log_warning "Claude models may not be available"
        fi
    else
        log_warning "Unable to verify Bedrock access"
        log_info "You may need to enable model access in AWS Console:"
        log_info "  1. Go to AWS Console → Bedrock"
        log_info "  2. Click 'Model access' → 'Manage model access'"
        log_info "  3. Enable 'Anthropic Claude 3 Sonnet'"
        echo ""
        confirm "Continue anyway?"
    fi
}

################################################################################
# Terraform Initialization
################################################################################

initialize_terraform() {
    print_step 4 "Initializing Terraform"

    cd "$TERRAFORM_DIR"

    log_info "Running terraform init..."
    if terraform init -upgrade 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Terraform initialized successfully"
    else
        log_error "Terraform initialization failed"
        exit 1
    fi

    # Validate configuration
    log_info "Validating Terraform configuration..."
    if terraform validate 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Configuration is valid"
    else
        log_error "Configuration validation failed"
        exit 1
    fi

    # Format check
    log_info "Checking code formatting..."
    terraform fmt -check -recursive || {
        log_warning "Code formatting issues found"
        log_info "Running terraform fmt to fix..."
        terraform fmt -recursive
        log_success "Code formatted"
    }
}

################################################################################
# Terraform Plan
################################################################################

plan_deployment() {
    print_step 5 "Planning Infrastructure Changes"

    cd "$TERRAFORM_DIR"

    if [ "$SKIP_PLAN" = true ]; then
        log_warning "Skipping plan (--skip-plan flag set)"
        return
    fi

    log_info "Running terraform plan..."
    log_info "This will show what resources will be created..."
    echo ""

    local plan_file="tfplan_${TIMESTAMP}"

    if terraform plan -out="$plan_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Plan completed successfully"

        echo ""
        print_separator
        log_info "Plan saved to: $plan_file"
        print_separator
        echo ""

        # Show summary
        log_info "Resources to be created:"
        terraform show "$plan_file" | grep "# aws_" | grep "will be created" | wc -l | xargs echo "  Count:"

        echo ""
        confirm "Review the plan above. Proceed with deployment?"

        # Clean up plan file
        rm -f "$plan_file"
    else
        log_error "Planning failed"
        rm -f "$plan_file"
        exit 1
    fi
}

################################################################################
# Terraform Apply
################################################################################

deploy_infrastructure() {
    print_step 6 "Deploying Infrastructure"

    cd "$TERRAFORM_DIR"

    log_info "Starting deployment..."
    log_warning "This will create AWS resources and may incur costs"
    echo ""

    local apply_opts=""
    if [ "$AUTO_APPROVE" = true ]; then
        apply_opts="-auto-approve"
        log_warning "Auto-approve enabled - deploying without confirmation"
    fi

    local start_time=$(date +%s)

    if terraform apply $apply_opts 2>&1 | tee -a "$LOG_FILE"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        echo ""
        log_success "Deployment completed successfully!"
        log_info "Deployment took ${duration} seconds"
    else
        log_error "Deployment failed"
        log_error "Check log file for details: $LOG_FILE"
        exit 1
    fi
}

################################################################################
# Display Results
################################################################################

display_results() {
    print_step 7 "Deployment Complete!"

    cd "$TERRAFORM_DIR"

    echo ""
    log_success "Legal Document Analysis Agent has been deployed!"
    echo ""

    print_separator
    log "${GREEN}${BOLD}Access Information:${NC}"
    print_separator
    echo ""

    # Get outputs
    local function_url=$(terraform output -raw function_url 2>/dev/null || echo "N/A")
    local function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "N/A")
    local log_group=$(terraform output -raw cloudwatch_log_group_name 2>/dev/null || echo "N/A")
    local region=$(terraform output -json deployment_info 2>/dev/null | grep -o '"region":"[^"]*"' | cut -d'"' -f4 || echo "us-east-1")

    log "${CYAN}Function URL:${NC}"
    log "${BOLD}$function_url${NC}"
    echo ""

    log "${CYAN}Function Name:${NC} $function_name"
    log "${CYAN}AWS Region:${NC} $region"
    log "${CYAN}Log Group:${NC} $log_group"
    echo ""

    print_separator
    log "${GREEN}${BOLD}Next Steps:${NC}"
    print_separator
    echo ""

    log "1. ${BOLD}Open the application:${NC}"
    log "   $function_url"
    echo ""

    log "2. ${BOLD}Test with sample contracts:${NC}"
    log "   - Click on sample contracts (NDA, Service Agreement, Employment)"
    log "   - Or paste your own legal documents"
    echo ""

    log "3. ${BOLD}Monitor logs:${NC}"
    log "   aws logs tail $log_group --follow --region $region"
    echo ""

    log "4. ${BOLD}View function details:${NC}"
    log "   aws lambda get-function --function-name $function_name --region $region"
    echo ""

    print_separator
    log "${YELLOW}${BOLD}Important:${NC} Ensure AWS Bedrock access is enabled"
    print_separator
    log "If AI analysis doesn't work:"
    log "  1. Go to AWS Console → Bedrock → Model access"
    log "  2. Enable 'Anthropic Claude 3 Sonnet'"
    log "  3. Wait for approval (usually instant)"
    echo ""

    print_separator
    log "${CYAN}${BOLD}Management Commands:${NC}"
    print_separator
    log "View outputs:    terraform output"
    log "Update:          ./terraform-deploy.sh"
    log "Destroy:         ./terraform-destroy.sh"
    log "View logs:       make logs"
    echo ""

    log_info "Deployment log saved to: $LOG_FILE"
    echo ""
}

################################################################################
# Error Handler
################################################################################

error_handler() {
    local line_number=$1
    echo ""
    log_error "Deployment failed at line $line_number"
    log_error "Check log file: $LOG_FILE"
    echo ""
    log_info "Common issues:"
    log "  - AWS credentials not configured"
    log "  - Insufficient IAM permissions"
    log "  - Region not supported"
    log "  - Terraform state lock (run: terraform force-unlock LOCK_ID)"
    echo ""
    exit 1
}

trap 'error_handler $LINENO' ERR

################################################################################
# Usage Information
################################################################################

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy the Legal Document Analysis Agent to AWS using Terraform.

OPTIONS:
    -a, --auto-approve    Skip confirmation prompts
    -s, --skip-plan       Skip the planning phase
    -v, --verbose         Enable verbose output
    -h, --help           Show this help message

EXAMPLES:
    # Interactive deployment
    $0

    # Quick deployment without prompts
    $0 --auto-approve

    # Deploy without planning phase
    $0 --skip-plan --auto-approve

PREREQUISITES:
    - Terraform installed (v1.0+)
    - AWS CLI installed and configured
    - AWS Bedrock access enabled (optional)

For more information, see terraform/README.md
EOF
    exit 0
}

################################################################################
# Parse Arguments
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--auto-approve)
                AUTO_APPROVE=true
                shift
                ;;
            -s|--skip-plan)
                SKIP_PLAN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                set -x
                shift
                ;;
            -h|--help)
                show_usage
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                ;;
        esac
    done
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse command line arguments
    parse_arguments "$@"

    # Clear screen and show banner
    clear
    print_banner

    log_info "Starting deployment at $(date)"
    log_info "Log file: $LOG_FILE"
    echo ""

    # Execute deployment steps
    check_prerequisites
    setup_configuration
    check_bedrock_access
    initialize_terraform
    plan_deployment
    deploy_infrastructure
    display_results

    # Success
    echo ""
    log_success "${BOLD}Deployment completed successfully!${NC}"
    echo ""
}

# Run main function
main "$@"
