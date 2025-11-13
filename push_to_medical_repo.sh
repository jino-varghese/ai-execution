#!/bin/bash

# ============================================================================
# Automated Script to Push Medical Diagnosis Code to New Repository
# ============================================================================
# Target: https://github.com/jino-varghese/AI-Powered-Medical-Diagnosis.git
#
# This script automates pushing the medical diagnosis project to a dedicated
# repository while preserving all commits and history.
#
# Usage:
#   chmod +x push_to_medical_repo.sh
#   ./push_to_medical_repo.sh
# ============================================================================

set -e  # Exit on any error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
TARGET_REPO="https://github.com/jino-varghese/AI-Powered-Medical-Diagnosis.git"
SOURCE_BRANCH="claude/read-documentation-01UcxE4w5cTCN6LnEpgpp2sV"
TARGET_BRANCH="main"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Push Medical Diagnosis Code to New Repository              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Verify we're in the right directory
# ============================================================================
echo -e "${YELLOW}[1/6] Verifying repository...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo "Please run this script from the ai-execution repository root"
    exit 1
fi

# Check if we're in ai-execution repo
if ! git remote -v | grep -q "ai-execution"; then
    echo -e "${RED}❌ Error: Not in ai-execution repository${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Repository verified${NC}"
echo ""

# ============================================================================
# Step 2: Checkout the medical diagnosis branch
# ============================================================================
echo -e "${YELLOW}[2/6] Checking out medical diagnosis branch...${NC}"

# Fetch latest changes
git fetch origin

# Checkout the branch
if git checkout ${SOURCE_BRANCH}; then
    echo -e "${GREEN}✅ Branch checked out: ${SOURCE_BRANCH}${NC}"
else
    echo -e "${RED}❌ Error: Could not checkout branch${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Step 3: Add new remote (if not exists)
# ============================================================================
echo -e "${YELLOW}[3/6] Adding remote repository...${NC}"

# Check if remote already exists
if git remote -v | grep -q "medical-diagnosis"; then
    echo "Remote 'medical-diagnosis' already exists, updating URL..."
    git remote set-url medical-diagnosis ${TARGET_REPO}
else
    git remote add medical-diagnosis ${TARGET_REPO}
fi

echo -e "${GREEN}✅ Remote added: ${TARGET_REPO}${NC}"
echo ""

# ============================================================================
# Step 4: Show files to be pushed
# ============================================================================
echo -e "${YELLOW}[4/6] Files to be pushed:${NC}"
echo ""
echo "📦 Application Files:"
echo "  ✅ medical_diagnosis_lambda.py"
echo "  ✅ medical_requirements.txt"
echo ""
echo "🔧 Deployment Scripts:"
echo "  ✅ deploy_medical_app.sh"
echo "  ✅ cleanup_medical_app.sh"
echo ""
echo "🏗️ Terraform (IaC):"
echo "  ✅ terraform/main.tf"
echo "  ✅ terraform/variables.tf"
echo "  ✅ terraform/outputs.tf"
echo "  ✅ terraform/versions.tf"
echo "  ✅ terraform/terraform.tfvars.example"
echo "  ✅ terraform/.gitignore"
echo ""
echo "📚 Documentation:"
echo "  ✅ MEDICAL_APP_README.md"
echo "  ✅ TERRAFORM_DEPLOYMENT.md"
echo "  ✅ DEPLOYMENT_COMPARISON.md"
echo "  ✅ PUSH_TO_NEW_REPO.md"
echo "  ✅ Capstone-project-description.docx"
echo ""

# ============================================================================
# Step 5: Confirm push
# ============================================================================
echo -e "${YELLOW}[5/6] Ready to push...${NC}"
echo ""
echo "Source: ${SOURCE_BRANCH}"
echo "Target: ${TARGET_REPO}"
echo "Branch: ${TARGET_BRANCH}"
echo ""
read -p "Continue with push? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Push cancelled.${NC}"
    exit 0
fi

# ============================================================================
# Step 6: Push to new repository
# ============================================================================
echo ""
echo -e "${YELLOW}[6/6] Pushing to new repository...${NC}"
echo ""

# Try to push
if git push medical-diagnosis ${SOURCE_BRANCH}:${TARGET_BRANCH}; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  🎉 PUSH SUCCESSFUL! 🎉                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📍 Repository URL:${NC}"
    echo -e "${GREEN}${TARGET_REPO}${NC}"
    echo ""
    echo -e "${BLUE}🌐 View on GitHub:${NC}"
    echo "https://github.com/jino-varghese/AI-Powered-Medical-Diagnosis"
    echo ""
    echo -e "${BLUE}🚀 Next Steps:${NC}"
    echo "  1. Visit the repository URL above"
    echo "  2. Verify all files are present"
    echo "  3. Update repository description and topics"
    echo "  4. Test deployment from the new repository"
    echo ""
    echo -e "${BLUE}📦 Clone the new repository:${NC}"
    echo "  git clone ${TARGET_REPO}"
    echo ""
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                     PUSH FAILED                               ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Possible reasons:${NC}"
    echo "  1. Authentication required - Run: gh auth login"
    echo "  2. No write access to repository"
    echo "  3. Network connection issue"
    echo ""
    echo -e "${YELLOW}Try these solutions:${NC}"
    echo ""
    echo "  Option 1: Use GitHub CLI"
    echo "    gh auth login"
    echo "    ./push_to_medical_repo.sh"
    echo ""
    echo "  Option 2: Use SSH instead of HTTPS"
    echo "    git remote set-url medical-diagnosis git@github.com:jino-varghese/AI-Powered-Medical-Diagnosis.git"
    echo "    ./push_to_medical_repo.sh"
    echo ""
    echo "  Option 3: Manual push"
    echo "    git push medical-diagnosis ${SOURCE_BRANCH}:${TARGET_BRANCH}"
    echo ""
    echo "See PUSH_TO_NEW_REPO.md for detailed instructions"
    echo ""
    exit 1
fi
