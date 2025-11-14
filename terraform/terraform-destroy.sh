#!/bin/bash

################################################################################
# Legal Document Analyzer - Terraform Destroy Script
#
# This script safely destroys all AWS resources created by Terraform:
# - Confirms destruction with user
# - Shows what will be destroyed
# - Performs cleanup
# - Provides summary
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
LOG_FILE="${TERRAFORM_DIR}/destroy_${TIMESTAMP}.log"

# Destruction options
AUTO_APPROVE=false
FORCE=false
VERBOSE=false

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${RED}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║    Legal Document Analysis Agent - Terraform Destroy      ║"
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
    read -p "Type 'yes' to confirm: " -r
    echo
    if [[ ! $REPLY = "yes" ]]; then
        log_error "Destruction cancelled by user"
        exit 1
    fi
}

################################################################################
# Check Prerequisites
################################################################################

check_prerequisites() {
    print_step 1 "Checking Prerequisites"

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi
    log_success "Terraform is installed"

    # Check if in correct directory
    if [ ! -f "main.tf" ]; then
        log_error "main.tf not found. Are you in the terraform directory?"
        exit 1
    fi
    log_success "Terraform configuration found"

    # Check for state file
    if [ ! -f "terraform.tfstate" ] && [ ! -f ".terraform/terraform.tfstate" ]; then
        log_warning "No terraform state file found"
        log_info "This might mean no infrastructure is deployed"

        if [ "$FORCE" = false ]; then
            confirm "Continue anyway?"
        fi
    else
        log_success "Terraform state found"
    fi
}

################################################################################
# Show Current Infrastructure
################################################################################

show_current_infrastructure() {
    print_step 2 "Current Infrastructure"

    cd "$TERRAFORM_DIR"

    log_info "Retrieving current infrastructure state..."
    echo ""

    # Get current outputs
    if terraform output &> /dev/null; then
        print_separator
        log "${CYAN}${BOLD}Current Deployment:${NC}"
        print_separator
        echo ""

        local function_url=$(terraform output -raw function_url 2>/dev/null || echo "N/A")
        local function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "N/A")
        local log_group=$(terraform output -raw cloudwatch_log_group_name 2>/dev/null || echo "N/A")

        log "${YELLOW}Function URL:${NC} $function_url"
        log "${YELLOW}Function Name:${NC} $function_name"
        log "${YELLOW}Log Group:${NC} $log_group"
        echo ""
    else
        log_warning "Unable to retrieve current outputs"
    fi

    # List resources
    log_info "Resources currently managed by Terraform:"
    echo ""

    if terraform state list 2>/dev/null | tee -a "$LOG_FILE"; then
        local resource_count=$(terraform state list 2>/dev/null | wc -l)
        echo ""
        log_info "Total resources: $resource_count"
    else
        log_warning "Unable to list resources"
    fi
}

################################################################################
# Plan Destruction
################################################################################

plan_destruction() {
    print_step 3 "Planning Destruction"

    cd "$TERRAFORM_DIR"

    log_info "Generating destruction plan..."
    log_warning "This will show what will be PERMANENTLY DELETED"
    echo ""

    if terraform plan -destroy 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Destruction plan generated"
    else
        log_error "Failed to generate destruction plan"
        exit 1
    fi

    echo ""
    print_separator
    log "${RED}${BOLD}⚠️  WARNING: This action cannot be undone!${NC}"
    print_separator
    echo ""

    log_warning "The following will be permanently deleted:"
    log "  • Lambda function and all its code"
    log "  • IAM roles and policies"
    log "  • CloudWatch log groups and all logs"
    log "  • Function URL endpoint (will stop working)"
    echo ""
}

################################################################################
# Backup Information
################################################################################

backup_information() {
    print_step 4 "Backing Up Information"

    cd "$TERRAFORM_DIR"

    local backup_file="backup_${TIMESTAMP}.txt"

    log_info "Saving current configuration to $backup_file..."

    {
        echo "========================================"
        echo "Legal Document Analyzer - Backup"
        echo "Timestamp: $(date)"
        echo "========================================"
        echo ""
        echo "OUTPUTS:"
        echo "--------"
        terraform output 2>/dev/null || echo "No outputs available"
        echo ""
        echo "RESOURCES:"
        echo "----------"
        terraform state list 2>/dev/null || echo "No resources found"
        echo ""
        echo "STATE:"
        echo "------"
        terraform show 2>/dev/null || echo "No state available"
    } > "$backup_file"

    if [ -f "$backup_file" ]; then
        log_success "Backup saved to: $backup_file"
    else
        log_warning "Could not create backup file"
    fi
}

################################################################################
# Destroy Infrastructure
################################################################################

destroy_infrastructure() {
    print_step 5 "Destroying Infrastructure"

    cd "$TERRAFORM_DIR"

    echo ""
    log_error "${BOLD}FINAL WARNING: All resources will be permanently deleted!${NC}"
    echo ""

    if [ "$AUTO_APPROVE" = false ]; then
        print_separator
        read -p "Type the function name to confirm destruction: " -r
        echo ""

        local function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "unknown")

        if [[ ! $REPLY = "$function_name" ]]; then
            log_error "Function name doesn't match. Destruction cancelled."
            exit 1
        fi
    fi

    log_warning "Starting destruction..."
    echo ""

    local destroy_opts=""
    if [ "$AUTO_APPROVE" = true ]; then
        destroy_opts="-auto-approve"
        log_warning "Auto-approve enabled - destroying without further confirmation"
    fi

    local start_time=$(date +%s)

    if terraform destroy $destroy_opts 2>&1 | tee -a "$LOG_FILE"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        echo ""
        log_success "Destruction completed successfully!"
        log_info "Destruction took ${duration} seconds"
    else
        log_error "Destruction failed"
        log_error "Some resources may still exist. Check AWS Console."
        log_error "Check log file for details: $LOG_FILE"
        exit 1
    fi
}

################################################################################
# Cleanup Local Files
################################################################################

cleanup_local_files() {
    print_step 6 "Cleaning Up Local Files"

    cd "$TERRAFORM_DIR"

    log_info "Cleaning up Terraform files..."

    local cleaned=false

    # Remove state files (optional - ask user)
    if [ -f "terraform.tfstate" ] || [ -f "terraform.tfstate.backup" ]; then
        if [ "$AUTO_APPROVE" = false ]; then
            echo ""
            read -p "Remove terraform state files? (yes/no): " -r
            echo ""
            if [[ $REPLY =~ ^[Yy]es$ ]]; then
                rm -f terraform.tfstate terraform.tfstate.backup
                log_success "Removed state files"
                cleaned=true
            fi
        else
            log_warning "Keeping state files (use --force to remove)"
        fi
    fi

    # Remove lock file
    if [ -f ".terraform.lock.hcl" ]; then
        if [ "$FORCE" = true ]; then
            rm -f .terraform.lock.hcl
            log_success "Removed lock file"
            cleaned=true
        fi
    fi

    # Remove .terraform directory
    if [ -d ".terraform" ]; then
        if [ "$FORCE" = true ]; then
            rm -rf .terraform
            log_success "Removed .terraform directory"
            cleaned=true
        fi
    fi

    # Remove zip files
    if ls *.zip 1> /dev/null 2>&1; then
        rm -f *.zip
        log_success "Removed deployment packages"
        cleaned=true
    fi

    if [ "$cleaned" = false ]; then
        log_info "No local files removed (use --force for deep clean)"
    fi
}

################################################################################
# Verify Destruction
################################################################################

verify_destruction() {
    print_step 7 "Verifying Destruction"

    cd "$TERRAFORM_DIR"

    log_info "Verifying all resources are destroyed..."

    # Check state
    local remaining_resources=$(terraform state list 2>/dev/null | wc -l)

    if [ "$remaining_resources" -eq 0 ]; then
        log_success "No resources remaining in state"
    else
        log_warning "$remaining_resources resources still in state"
        log_info "Remaining resources:"
        terraform state list 2>/dev/null | while read -r resource; do
            log "  ${YELLOW}$resource${NC}"
        done
    fi

    # Try to verify in AWS (optional)
    if command -v aws &> /dev/null; then
        log_info "Checking AWS for orphaned resources..."

        local function_name=$(grep 'lambda_function_name' terraform.tfvars 2>/dev/null | cut -d'"' -f2 || echo "legal-document-analyzer")
        local region=$(grep 'aws_region' terraform.tfvars 2>/dev/null | cut -d'"' -f2 || echo "us-east-1")

        if aws lambda get-function --function-name "$function_name" --region "$region" &> /dev/null; then
            log_warning "Lambda function still exists in AWS!"
            log_info "You may need to delete it manually"
        else
            log_success "Lambda function confirmed deleted"
        fi
    fi
}

################################################################################
# Display Summary
################################################################################

display_summary() {
    print_step 8 "Destruction Complete"

    echo ""
    log_success "${BOLD}All infrastructure has been destroyed!${NC}"
    echo ""

    print_separator
    log "${GREEN}${BOLD}Summary:${NC}"
    print_separator
    echo ""

    log "${CYAN}What was deleted:${NC}"
    log "  ✓ Lambda function"
    log "  ✓ IAM role and policies"
    log "  ✓ Function URL endpoint"
    log "  ✓ CloudWatch log group"
    echo ""

    log "${CYAN}What was preserved:${NC}"
    log "  • Source code (lambda_function.py)"
    log "  • Terraform configuration files"
    log "  • Backup file (if created)"
    log "  • Destruction log: $LOG_FILE"
    echo ""

    print_separator
    log "${YELLOW}${BOLD}Next Steps:${NC}"
    print_separator
    echo ""

    log "To redeploy:"
    log "  ./terraform-deploy.sh"
    echo ""

    log "To verify cleanup:"
    log "  aws lambda list-functions --region us-east-1"
    echo ""

    log "For complete cleanup (remove all Terraform files):"
    log "  rm -rf .terraform terraform.tfstate* .terraform.lock.hcl *.zip"
    echo ""
}

################################################################################
# Error Handler
################################################################################

error_handler() {
    local line_number=$1
    echo ""
    log_error "Destruction failed at line $line_number"
    log_error "Check log file: $LOG_FILE"
    echo ""
    log_warning "Some resources may still exist in AWS"
    log_info "Please check AWS Console and clean up manually if needed"
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

Destroy all AWS resources created by Terraform for the Legal Document Analysis Agent.

OPTIONS:
    -a, --auto-approve    Skip confirmation prompts (DANGEROUS!)
    -f, --force          Force cleanup of all local files
    -v, --verbose        Enable verbose output
    -h, --help           Show this help message

EXAMPLES:
    # Interactive destruction (recommended)
    $0

    # Quick destruction without prompts (use with caution!)
    $0 --auto-approve

    # Destroy and clean up all local files
    $0 --force

WARNING:
    This will permanently delete all deployed AWS resources.
    This action cannot be undone!

WHAT GETS DELETED:
    - Lambda function
    - IAM roles and policies
    - CloudWatch log groups
    - Function URL endpoint

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
            -f|--force)
                FORCE=true
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

    log_warning "${BOLD}This script will PERMANENTLY DELETE all deployed infrastructure!${NC}"
    log_info "Starting destruction at $(date)"
    log_info "Log file: $LOG_FILE"
    echo ""

    # Final safety check
    if [ "$AUTO_APPROVE" = false ]; then
        echo ""
        print_separator
        log_error "${BOLD}⚠️  DANGER ZONE ⚠️${NC}"
        print_separator
        echo ""
        log_warning "You are about to destroy all AWS resources for the Legal Document Analyzer."
        log_warning "This includes:"
        log "  • Lambda function and all code"
        log "  • IAM roles and policies"
        log "  • CloudWatch logs (all historical data)"
        log "  • Function URL (endpoint will stop working)"
        echo ""
        confirm "Are you absolutely sure you want to continue?"
        echo ""
    fi

    # Execute destruction steps
    check_prerequisites
    show_current_infrastructure
    plan_destruction
    backup_information
    destroy_infrastructure
    cleanup_local_files
    verify_destruction
    display_summary

    # Success
    echo ""
    log_success "${BOLD}Destruction completed successfully!${NC}"
    echo ""
}

# Run main function
main "$@"
