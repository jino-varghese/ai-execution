#!/bin/bash

################################################################################
# Legal Document Analyzer - Unified Terraform Management Script
#
# This script provides a convenient interface for managing infrastructure:
# - Deploy infrastructure
# - Destroy infrastructure
# - View current state
# - Manage resources
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

################################################################################
# Helper Functions
################################################################################

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║     Legal Document Analyzer - Terraform Management        ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_menu() {
    echo -e "${BOLD}${BLUE}Main Menu:${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} Deploy Infrastructure"
    echo -e "  ${GREEN}2)${NC} Destroy Infrastructure"
    echo -e "  ${GREEN}3)${NC} View Current State"
    echo -e "  ${GREEN}4)${NC} View Outputs"
    echo -e "  ${GREEN}5)${NC} View Logs"
    echo -e "  ${GREEN}6)${NC} Validate Configuration"
    echo -e "  ${GREEN}7)${NC} Plan Changes"
    echo -e "  ${GREEN}8)${NC} Format Code"
    echo -e "  ${GREEN}9)${NC} Open Application"
    echo -e "  ${RED}0)${NC} Exit"
    echo ""
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

press_enter() {
    echo ""
    read -p "Press Enter to continue..."
}

################################################################################
# Menu Actions
################################################################################

deploy_infrastructure() {
    echo -e "${CYAN}${BOLD}Deploying Infrastructure...${NC}"
    echo ""

    if [ -f "${SCRIPT_DIR}/terraform-deploy.sh" ]; then
        bash "${SCRIPT_DIR}/terraform-deploy.sh" "$@"
    else
        log_error "terraform-deploy.sh not found!"
        exit 1
    fi

    press_enter
}

destroy_infrastructure() {
    echo -e "${RED}${BOLD}Destroying Infrastructure...${NC}"
    echo ""

    if [ -f "${SCRIPT_DIR}/terraform-destroy.sh" ]; then
        bash "${SCRIPT_DIR}/terraform-destroy.sh" "$@"
    else
        log_error "terraform-destroy.sh not found!"
        exit 1
    fi

    press_enter
}

view_state() {
    echo -e "${CYAN}${BOLD}Current Infrastructure State:${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    if [ ! -f "terraform.tfstate" ] && [ ! -f ".terraform/terraform.tfstate" ]; then
        log_error "No state file found. Infrastructure may not be deployed."
    else
        log_info "Resources managed by Terraform:"
        echo ""
        terraform state list 2>/dev/null || log_error "Failed to list resources"
    fi

    press_enter
}

view_outputs() {
    echo -e "${CYAN}${BOLD}Terraform Outputs:${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    if terraform output &> /dev/null; then
        terraform output

        echo ""
        echo -e "${GREEN}Quick Access:${NC}"
        local function_url=$(terraform output -raw function_url 2>/dev/null)
        if [ ! -z "$function_url" ]; then
            echo -e "Function URL: ${BOLD}$function_url${NC}"
        fi
    else
        log_error "No outputs available. Is infrastructure deployed?"
    fi

    press_enter
}

view_logs() {
    echo -e "${CYAN}${BOLD}Viewing CloudWatch Logs...${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    local log_group=$(terraform output -raw cloudwatch_log_group_name 2>/dev/null)
    local region=$(terraform output -json deployment_info 2>/dev/null | grep -o '"region":"[^"]*"' | cut -d'"' -f4 || echo "us-east-1")

    if [ ! -z "$log_group" ]; then
        log_info "Log group: $log_group"
        log_info "Region: $region"
        echo ""
        log_info "Tailing logs (Ctrl+C to stop)..."
        echo ""

        if command -v aws &> /dev/null; then
            aws logs tail "$log_group" --follow --region "$region" || log_error "Failed to tail logs"
        else
            log_error "AWS CLI not installed"
        fi
    else
        log_error "Cannot retrieve log group. Is infrastructure deployed?"
    fi

    press_enter
}

validate_configuration() {
    echo -e "${CYAN}${BOLD}Validating Terraform Configuration...${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    log_info "Running terraform validate..."
    if terraform validate; then
        log_success "Configuration is valid!"
    else
        log_error "Configuration validation failed"
    fi

    press_enter
}

plan_changes() {
    echo -e "${CYAN}${BOLD}Planning Infrastructure Changes...${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    log_info "Running terraform plan..."
    terraform plan || log_error "Plan failed"

    press_enter
}

format_code() {
    echo -e "${CYAN}${BOLD}Formatting Terraform Code...${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    log_info "Running terraform fmt..."
    if terraform fmt -recursive; then
        log_success "Code formatted successfully!"
    else
        log_error "Formatting failed"
    fi

    press_enter
}

open_application() {
    echo -e "${CYAN}${BOLD}Opening Application...${NC}"
    echo ""

    cd "$SCRIPT_DIR"

    local function_url=$(terraform output -raw function_url 2>/dev/null)

    if [ ! -z "$function_url" ]; then
        log_info "Opening: $function_url"

        # Try to open in default browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "$function_url"
        elif command -v open &> /dev/null; then
            open "$function_url"
        elif command -v start &> /dev/null; then
            start "$function_url"
        else
            echo ""
            echo -e "${GREEN}Copy this URL to your browser:${NC}"
            echo -e "${BOLD}$function_url${NC}"
        fi

        log_success "Done!"
    else
        log_error "No function URL found. Is infrastructure deployed?"
    fi

    press_enter
}

################################################################################
# Main Menu Loop
################################################################################

show_menu() {
    while true; do
        print_banner
        print_menu

        read -p "Select an option [0-9]: " choice
        echo ""

        case $choice in
            1)
                deploy_infrastructure
                ;;
            2)
                destroy_infrastructure
                ;;
            3)
                view_state
                ;;
            4)
                view_outputs
                ;;
            5)
                view_logs
                ;;
            6)
                validate_configuration
                ;;
            7)
                plan_changes
                ;;
            8)
                format_code
                ;;
            9)
                open_application
                ;;
            0)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                log_error "Invalid option. Please select 0-9."
                press_enter
                ;;
        esac
    done
}

################################################################################
# Command Line Mode
################################################################################

show_usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Unified management script for Legal Document Analyzer infrastructure.

COMMANDS:
    deploy              Deploy infrastructure
    destroy             Destroy infrastructure
    state               View current state
    outputs             View outputs
    logs                View CloudWatch logs
    validate            Validate configuration
    plan                Plan changes
    format              Format code
    open                Open application in browser
    menu                Show interactive menu (default)

OPTIONS:
    --auto-approve      Skip confirmation prompts
    --help              Show this help message

EXAMPLES:
    # Interactive menu
    $0

    # Deploy directly
    $0 deploy

    # Deploy without prompts
    $0 deploy --auto-approve

    # Destroy infrastructure
    $0 destroy

    # View current state
    $0 state

For more information, see terraform/README.md
EOF
    exit 0
}

################################################################################
# Main Execution
################################################################################

main() {
    cd "$SCRIPT_DIR"

    # If no arguments, show interactive menu
    if [ $# -eq 0 ]; then
        show_menu
        exit 0
    fi

    # Parse command
    local command=$1
    shift

    case $command in
        deploy)
            deploy_infrastructure "$@"
            ;;
        destroy)
            destroy_infrastructure "$@"
            ;;
        state)
            view_state
            ;;
        outputs)
            view_outputs
            ;;
        logs)
            view_logs
            ;;
        validate)
            validate_configuration
            ;;
        plan)
            plan_changes
            ;;
        format)
            format_code
            ;;
        open)
            open_application
            ;;
        menu)
            show_menu
            ;;
        --help|-h|help)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_usage
            ;;
    esac
}

# Run main function
main "$@"
