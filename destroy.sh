#!/bin/bash

################################################################################
# AI Medical Diagnosis System - AWS Infrastructure Cleanup Script
################################################################################
# This script destroys all AWS resources created by Terraform.
#
# ⚠️  WARNING: This will permanently delete all resources!
#     - Lambda function
#     - CloudWatch logs
#     - IAM roles and policies
#
# Usage: ./destroy.sh
################################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
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

log_danger() {
    echo -e "${RED}[DANGER]${NC} $1"
}

print_banner() {
    echo ""
    echo "============================================================"
    echo "  🗑️  AI Medical Diagnosis System - Infrastructure Cleanup"
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

    # Check Terraform
    if command_exists terraform; then
        log_success "Terraform is installed"
    else
        log_error "Terraform is not installed"
        all_ok=false
    fi

    # Check AWS CLI
    if command_exists aws; then
        log_success "AWS CLI is installed"
    else
        log_warning "AWS CLI is not installed (optional for verification)"
    fi

    if [ "$all_ok" = false ]; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    print_separator
}

# Check if Terraform is initialized
check_terraform_state() {
    log_info "Checking Terraform state..."

    if [ ! -d ".terraform" ]; then
        log_error "Terraform not initialized. No infrastructure to destroy."
        log_info "Run './deploy.sh' first to create infrastructure"
        exit 1
    fi

    if [ ! -f "terraform.tfstate" ]; then
        log_warning "No terraform.tfstate file found"
        log_warning "This might mean infrastructure was never deployed"

        read -p "$(echo -e ${YELLOW}Do you want to continue anyway? [y/N]:${NC} )" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleanup cancelled"
            exit 0
        fi
    else
        log_success "Terraform state found"
    fi

    print_separator
}

# Show current infrastructure
show_current_infrastructure() {
    log_info "Analyzing current infrastructure..."
    echo ""

    # Try to get outputs
    if terraform output >/dev/null 2>&1; then
        local function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "N/A")
        local region=$(terraform output -raw deployment_region 2>/dev/null || echo "N/A")
        local account_id=$(terraform output -raw aws_account_id 2>/dev/null || echo "N/A")

        echo "📋 Resources to be destroyed:"
        echo "   - Lambda Function: $function_name"
        echo "   - Region: $region"
        echo "   - Account: $account_id"
        echo "   - IAM Role"
        echo "   - CloudWatch Log Group"
        echo "   - Lambda Function URL"
        echo ""
    else
        log_warning "Could not retrieve infrastructure details"
        echo ""
    fi

    print_separator
}

# Display warning
show_warning() {
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}                    ⚠️  WARNING ⚠️${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo -e "${YELLOW}This action will PERMANENTLY DELETE all AWS resources:${NC}"
    echo ""
    echo "  ❌ Lambda function and all code"
    echo "  ❌ CloudWatch log groups and ALL logs"
    echo "  ❌ IAM roles and policies"
    echo "  ❌ Lambda function URL (public endpoint)"
    echo ""
    echo -e "${RED}This action CANNOT be undone!${NC}"
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo ""
}

# Safety confirmation
confirm_destruction() {
    log_danger "Multiple confirmations required for safety"
    echo ""

    # First confirmation
    read -p "$(echo -e ${RED}Are you sure you want to destroy all resources? [yes/NO]:${NC} )" -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Cleanup cancelled (first confirmation failed)"
        exit 0
    fi

    # Second confirmation
    echo -e "${YELLOW}Second confirmation required...${NC}"
    read -p "$(echo -e ${RED}Type 'DESTROY' to confirm destruction:${NC} )" -r
    echo
    if [[ $REPLY != "DESTROY" ]]; then
        log_info "Cleanup cancelled (second confirmation failed)"
        exit 0
    fi

    # Final countdown
    echo -e "${RED}Starting destruction in 5 seconds...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to cancel${NC}"
    for i in 5 4 3 2 1; do
        echo -n "$i... "
        sleep 1
    done
    echo ""
    echo ""

    print_separator
}

# Create backup of state
backup_state() {
    log_info "Creating backup of Terraform state..."

    if [ -f "terraform.tfstate" ]; then
        local backup_file="terraform.tfstate.backup.$(date +%Y%m%d_%H%M%S)"
        cp terraform.tfstate "$backup_file"
        log_success "State backed up to: $backup_file"
    else
        log_warning "No state file to backup"
    fi

    print_separator
}

# Run Terraform destroy
terraform_destroy() {
    log_info "Destroying AWS infrastructure..."
    echo ""

    if terraform destroy -auto-approve; then
        log_success "All resources destroyed successfully"
    else
        log_error "Terraform destroy failed"
        log_warning "Some resources may still exist in AWS"
        exit 1
    fi

    print_separator
}

# Cleanup local files
cleanup_local_files() {
    log_info "Cleaning up local Terraform files..."

    # Ask about state files
    read -p "$(echo -e ${YELLOW}Remove Terraform state files? [y/N]:${NC} )" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f terraform.tfstate
        rm -f terraform.tfstate.backup
        rm -f .terraform.lock.hcl
        rm -f tfplan
        rm -f .deployment_url
        log_success "State files removed"
    else
        log_info "Keeping state files"
    fi

    # Ask about .terraform directory
    read -p "$(echo -e ${YELLOW}Remove .terraform directory? [y/N]:${NC} )" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .terraform
        log_success ".terraform directory removed"
    else
        log_info "Keeping .terraform directory"
    fi

    print_separator
}

# Verify destruction
verify_destruction() {
    log_info "Verifying destruction..."

    if command_exists aws; then
        local function_name=$(grep 'project_name' terraform.tfvars 2>/dev/null | cut -d'=' -f2 | tr -d ' "' || echo "medical-diagnosis")
        local environment=$(grep 'environment' terraform.tfvars 2>/dev/null | cut -d'=' -f2 | tr -d ' "' || echo "dev")
        local full_name="${function_name}-${environment}"

        if aws lambda get-function --function-name "$full_name" >/dev/null 2>&1; then
            log_warning "Lambda function still exists in AWS!"
            log_warning "You may need to delete it manually"
        else
            log_success "Lambda function confirmed deleted"
        fi
    else
        log_info "AWS CLI not available for verification"
    fi

    print_separator
}

# Show completion message
show_completion() {
    echo ""
    echo "============================================================"
    echo "  ✅ CLEANUP COMPLETED"
    echo "============================================================"
    echo ""
    echo "All AWS resources have been destroyed."
    echo ""
    echo "💡 Next Steps:"
    echo "   - Verify deletion in AWS Console"
    echo "   - Check for any remaining resources"
    echo "   - Review backup state files if needed"
    echo ""
    echo "To redeploy, run: ./deploy.sh"
    echo ""
    echo "============================================================"
    echo ""
}

# Main cleanup flow
main() {
    print_banner

    # Change to script directory
    cd "$(dirname "$0")"

    # Run cleanup steps
    check_prerequisites
    check_terraform_state
    show_current_infrastructure
    show_warning
    confirm_destruction
    backup_state
    terraform_destroy
    verify_destruction
    cleanup_local_files
    show_completion

    log_success "Infrastructure cleanup completed! 🗑️"
    echo ""
}

# Trap errors
trap 'log_error "Cleanup failed at line $LINENO"' ERR

# Run main function
main "$@"
