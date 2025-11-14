# Terraform Shell Scripts Guide

Three powerful shell scripts for managing your Legal Document Analyzer infrastructure.

## 📋 Available Scripts

### 1. `terraform.sh` - Unified Management (Recommended)

Interactive menu-driven interface for all operations.

**Usage:**
```bash
# Interactive menu
./terraform.sh

# Direct commands
./terraform.sh deploy
./terraform.sh destroy
./terraform.sh state
./terraform.sh outputs
./terraform.sh logs
./terraform.sh validate
./terraform.sh plan
./terraform.sh format
./terraform.sh open
```

**Features:**
- ✅ User-friendly menu interface
- ✅ All operations in one script
- ✅ Quick access to common tasks
- ✅ Browser integration

### 2. `terraform-deploy.sh` - Deployment Script

Comprehensive deployment with checks and validation.

**Usage:**
```bash
# Interactive deployment (recommended)
./terraform-deploy.sh

# Quick deployment
./terraform-deploy.sh --auto-approve

# Skip planning phase
./terraform-deploy.sh --skip-plan

# Verbose output
./terraform-deploy.sh --verbose

# Combined options
./terraform-deploy.sh --auto-approve --verbose
```

**What it does:**
1. ✅ Checks prerequisites (Terraform, AWS CLI, credentials)
2. ✅ Sets up configuration (creates terraform.tfvars if needed)
3. ✅ Checks AWS Bedrock access
4. ✅ Initializes Terraform
5. ✅ Plans infrastructure changes
6. ✅ Deploys to AWS
7. ✅ Displays access information and next steps

**Output:**
- Function URL for immediate access
- CloudWatch log group name
- Deployment summary
- Useful commands
- Log file for troubleshooting

### 3. `terraform-destroy.sh` - Destruction Script

Safe destruction with multiple confirmations.

**Usage:**
```bash
# Interactive destruction (recommended)
./terraform-destroy.sh

# Quick destruction (DANGEROUS!)
./terraform-destroy.sh --auto-approve

# Force cleanup of local files
./terraform-destroy.sh --force

# Verbose output
./terraform-destroy.sh --verbose
```

**What it does:**
1. ⚠️ Shows current infrastructure
2. ⚠️ Plans destruction (what will be deleted)
3. ⚠️ Backs up current state
4. ⚠️ Destroys infrastructure
5. ⚠️ Cleans up local files (optional)
6. ⚠️ Verifies destruction
7. ⚠️ Provides summary

**Safety features:**
- Multiple confirmation prompts
- Must type function name to confirm
- Creates backup before destruction
- Verifies resources are deleted
- Optional local file cleanup

## 🚀 Quick Start

### First Time Deployment

```bash
# Option 1: Interactive menu
./terraform.sh
# Select: 1) Deploy Infrastructure

# Option 2: Direct deploy
./terraform-deploy.sh
```

### View Your Application

```bash
# Option 1: Auto-open in browser
./terraform.sh open

# Option 2: Get URL
./terraform.sh outputs
```

### Monitor Logs

```bash
./terraform.sh logs
# Or
./terraform.sh
# Select: 5) View Logs
```

### Destroy Everything

```bash
# Option 1: Interactive
./terraform.sh destroy

# Option 2: Direct
./terraform-destroy.sh
```

## 📊 Common Workflows

### Development Workflow

```bash
# Deploy
./terraform-deploy.sh

# Test application
./terraform.sh open

# View logs
./terraform.sh logs

# Make changes to code
# ...

# Redeploy
./terraform-deploy.sh

# Destroy when done
./terraform-destroy.sh
```

### Production Workflow

```bash
# Validate configuration
./terraform.sh validate

# Review plan
./terraform.sh plan

# Deploy with logging
./terraform-deploy.sh --verbose

# Monitor
./terraform.sh logs
```

### Troubleshooting Workflow

```bash
# Check current state
./terraform.sh state

# View outputs
./terraform.sh outputs

# Check logs
./terraform.sh logs

# Validate configuration
./terraform.sh validate
```

## 🎯 Script Comparison

| Feature | terraform.sh | terraform-deploy.sh | terraform-destroy.sh |
|---------|--------------|---------------------|----------------------|
| Interactive menu | ✅ | ❌ | ❌ |
| Deploy infrastructure | ✅ | ✅ | ❌ |
| Destroy infrastructure | ✅ | ❌ | ✅ |
| View state | ✅ | ❌ | ✅ |
| View logs | ✅ | ❌ | ❌ |
| Validate config | ✅ | ✅ | ❌ |
| Prerequisite checks | ❌ | ✅ | ✅ |
| Bedrock check | ❌ | ✅ | ❌ |
| Backup creation | ❌ | ❌ | ✅ |
| Auto-approve option | ✅ | ✅ | ✅ |

## 🔧 Command Line Options

### terraform-deploy.sh

```
-a, --auto-approve    Skip confirmation prompts
-s, --skip-plan       Skip the planning phase
-v, --verbose         Enable verbose output
-h, --help           Show help message
```

### terraform-destroy.sh

```
-a, --auto-approve    Skip confirmation prompts
-f, --force          Force cleanup of all local files
-v, --verbose        Enable verbose output
-h, --help           Show help message
```

### terraform.sh

```
Commands:
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

Options:
  --auto-approve      Skip confirmation prompts
  --help              Show help message
```

## 📝 Log Files

All scripts create log files for troubleshooting:

- **Deploy:** `deployment_YYYYMMDD_HHMMSS.log`
- **Destroy:** `destroy_YYYYMMDD_HHMMSS.log`

These contain complete output and can help diagnose issues.

## 🔒 Safety Features

### Deployment Safety
- ✅ Prerequisite checks
- ✅ Configuration validation
- ✅ Plan review before apply
- ✅ Error handling with rollback
- ✅ Detailed logging

### Destruction Safety
- ⚠️ Multiple warnings
- ⚠️ Shows current infrastructure
- ⚠️ Must type function name to confirm
- ⚠️ Creates backup before destruction
- ⚠️ Verifies cleanup
- ⚠️ No auto-approve by default

## 🎨 Output Colors

Scripts use colored output for clarity:

- 🔵 **Blue:** Informational messages
- 🟢 **Green:** Success messages
- 🟡 **Yellow:** Warnings
- 🔴 **Red:** Errors
- 🟣 **Magenta:** Step headers
- 🔷 **Cyan:** Section headers

## 🐛 Troubleshooting

### Script won't run

```bash
# Make executable
chmod +x terraform/*.sh

# Verify
ls -la terraform/*.sh
```

### AWS credentials not working

```bash
# Reconfigure
aws configure

# Test
aws sts get-caller-identity
```

### Terraform not found

```bash
# Install Terraform
# macOS
brew install terraform

# Linux
wget https://terraform.io/downloads
```

### Stuck at confirmation

```bash
# Use auto-approve (with caution!)
./terraform-deploy.sh --auto-approve
```

### Need to see detailed output

```bash
# Use verbose mode
./terraform-deploy.sh --verbose
```

## 💡 Tips

1. **Always use `terraform.sh` for daily operations** - it's the easiest
2. **Review the plan before deploying** - understand what will be created
3. **Keep log files** - they're helpful for troubleshooting
4. **Use `--auto-approve` carefully** - it skips safety checks
5. **Test in dev before prod** - use different terraform.tfvars
6. **Monitor logs regularly** - catch issues early
7. **Clean up when done** - use destroy to avoid costs

## 📚 Examples

### Example 1: First Time Setup

```bash
# Clone repository
cd terraform

# Deploy
./terraform.sh deploy

# Wait for completion, then open
./terraform.sh open

# Test the application
# (paste a contract, click analyze)

# View logs to see it working
./terraform.sh logs
```

### Example 2: Update Deployment

```bash
# Edit configuration
nano terraform.tfvars

# Validate changes
./terraform.sh validate

# Plan changes
./terraform.sh plan

# Apply changes
./terraform.sh deploy
```

### Example 3: Complete Cleanup

```bash
# Destroy infrastructure
./terraform-destroy.sh

# Force cleanup of all files
./terraform-destroy.sh --force

# Verify nothing left
./terraform.sh state
```

## 🆘 Getting Help

```bash
# Script help
./terraform.sh --help
./terraform-deploy.sh --help
./terraform-destroy.sh --help

# Terraform help
terraform --help

# AWS help
aws help
```

## 📞 Support

If scripts fail:
1. Check the log file created
2. Verify prerequisites are installed
3. Check AWS credentials
4. Review Terraform state
5. Check AWS Console

---

**Scripts Version:** 1.0
**Last Updated:** 2025
**Compatibility:** Terraform 1.0+, AWS CLI 2.0+
