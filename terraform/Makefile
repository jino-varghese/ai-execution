.PHONY: help init plan apply destroy clean validate format check output logs

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Legal Document Analyzer - Terraform Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

init: ## Initialize Terraform
	@echo "$(BLUE)Initializing Terraform...$(NC)"
	@terraform init
	@echo "$(GREEN)✓ Terraform initialized$(NC)"

plan: ## Show execution plan
	@echo "$(BLUE)Planning infrastructure changes...$(NC)"
	@terraform plan
	@echo "$(GREEN)✓ Plan complete$(NC)"

apply: ## Apply Terraform configuration
	@echo "$(BLUE)Applying Terraform configuration...$(NC)"
	@terraform apply
	@echo "$(GREEN)✓ Infrastructure deployed$(NC)"
	@echo ""
	@echo "$(GREEN)Access your application at:$(NC)"
	@terraform output function_url

apply-auto: ## Apply without confirmation (use with caution)
	@echo "$(YELLOW)Auto-applying Terraform configuration...$(NC)"
	@terraform apply -auto-approve
	@echo "$(GREEN)✓ Infrastructure deployed$(NC)"

destroy: ## Destroy all resources
	@echo "$(RED)WARNING: This will destroy all infrastructure!$(NC)"
	@terraform destroy

destroy-auto: ## Destroy without confirmation (use with extreme caution)
	@echo "$(RED)Auto-destroying infrastructure...$(NC)"
	@terraform destroy -auto-approve

validate: ## Validate Terraform files
	@echo "$(BLUE)Validating Terraform configuration...$(NC)"
	@terraform validate
	@echo "$(GREEN)✓ Configuration is valid$(NC)"

format: ## Format Terraform files
	@echo "$(BLUE)Formatting Terraform files...$(NC)"
	@terraform fmt -recursive
	@echo "$(GREEN)✓ Files formatted$(NC)"

check: validate format ## Run validation and formatting

output: ## Show all outputs
	@terraform output

function-url: ## Show Function URL
	@echo "$(GREEN)Function URL:$(NC)"
	@terraform output -raw function_url
	@echo ""

open: ## Open Function URL in browser
	@echo "$(BLUE)Opening application in browser...$(NC)"
	@open $$(terraform output -raw function_url) || xdg-open $$(terraform output -raw function_url) || start $$(terraform output -raw function_url)

logs: ## View CloudWatch logs
	@echo "$(BLUE)Tailing Lambda logs...$(NC)"
	@aws logs tail $$(terraform output -raw cloudwatch_log_group_name) --follow

state: ## Show current state
	@terraform show

resources: ## List all resources
	@terraform state list

clean: ## Clean Terraform files
	@echo "$(YELLOW)Cleaning Terraform files...$(NC)"
	@rm -rf .terraform
	@rm -f .terraform.lock.hcl
	@rm -f terraform.tfstate
	@rm -f terraform.tfstate.backup
	@rm -f *.zip
	@echo "$(GREEN)✓ Cleaned$(NC)"

setup: ## Setup configuration from example
	@if [ ! -f terraform.tfvars ]; then \
		echo "$(BLUE)Creating terraform.tfvars from example...$(NC)"; \
		cp terraform.tfvars.example terraform.tfvars; \
		echo "$(GREEN)✓ Created terraform.tfvars$(NC)"; \
		echo "$(YELLOW)Please edit terraform.tfvars with your settings$(NC)"; \
	else \
		echo "$(YELLOW)terraform.tfvars already exists$(NC)"; \
	fi

cost: ## Estimate infrastructure costs (requires infracost)
	@if command -v infracost >/dev/null 2>&1; then \
		echo "$(BLUE)Estimating costs...$(NC)"; \
		infracost breakdown --path .; \
	else \
		echo "$(YELLOW)infracost not installed. Install with: brew install infracost$(NC)"; \
	fi

graph: ## Generate dependency graph (requires graphviz)
	@echo "$(BLUE)Generating dependency graph...$(NC)"
	@terraform graph | dot -Tpng > graph.png
	@echo "$(GREEN)✓ Graph saved to graph.png$(NC)"

refresh: ## Refresh Terraform state
	@echo "$(BLUE)Refreshing state...$(NC)"
	@terraform refresh

console: ## Open Terraform console
	@terraform console

import-lambda: ## Import existing Lambda function
	@echo "$(BLUE)Enter Lambda function name:$(NC)"
	@read function_name; \
	terraform import aws_lambda_function.legal_analyzer $$function_name

deploy: init validate apply ## Complete deployment workflow

update: format validate apply ## Update existing infrastructure

test: validate ## Run tests
	@echo "$(BLUE)Running Terraform tests...$(NC)"
	@terraform validate
	@echo "$(GREEN)✓ Tests passed$(NC)"
