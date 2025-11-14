# Terraform Deployment Checklist

Use this checklist to ensure a smooth deployment of the Legal Document Analysis Agent.

## Pre-Deployment Checklist

### ✅ Prerequisites

- [ ] Terraform installed (v1.0+)
  ```bash
  terraform version
  ```

- [ ] AWS CLI installed and configured
  ```bash
  aws sts get-caller-identity
  ```

- [ ] AWS account has necessary permissions
  - [ ] Create/manage Lambda functions
  - [ ] Create/manage IAM roles and policies
  - [ ] Create/manage CloudWatch log groups
  - [ ] Access to Bedrock (if using AI features)

- [ ] AWS Bedrock access enabled (if using AI)
  - [ ] Go to AWS Console → Bedrock
  - [ ] Model access → Manage model access
  - [ ] Enable Anthropic Claude 3 Sonnet
  - [ ] Wait for approval (usually instant)

### 📝 Configuration

- [ ] Created `terraform.tfvars` from example
  ```bash
  cp terraform.tfvars.example terraform.tfvars
  ```

- [ ] Reviewed and updated configuration values in `terraform.tfvars`
  - [ ] AWS region
  - [ ] Lambda function name
  - [ ] Memory size and timeout
  - [ ] CORS settings
  - [ ] Environment variables

- [ ] Reviewed security settings
  - [ ] Function URL authentication type
  - [ ] CORS allowed origins
  - [ ] CloudWatch alarm settings

## Deployment Checklist

### 🚀 Initial Deployment

- [ ] Initialize Terraform
  ```bash
  terraform init
  ```
  Expected: "Terraform has been successfully initialized!"

- [ ] Validate configuration
  ```bash
  terraform validate
  ```
  Expected: "Success! The configuration is valid."

- [ ] Format code (optional)
  ```bash
  terraform fmt
  ```

- [ ] Review execution plan
  ```bash
  terraform plan
  ```
  - [ ] Verify resources to be created (~6 resources)
  - [ ] Check resource names and configurations
  - [ ] Confirm no unexpected changes

- [ ] Apply configuration
  ```bash
  terraform apply
  ```
  - [ ] Review plan one more time
  - [ ] Type `yes` to confirm
  - [ ] Wait for completion (~2-3 minutes)

- [ ] Save outputs
  ```bash
  terraform output > deployment-info.txt
  ```

### ✅ Post-Deployment Verification

- [ ] Verify Function URL is accessible
  ```bash
  terraform output function_url
  ```

- [ ] Test in browser
  - [ ] Open Function URL
  - [ ] Page loads successfully
  - [ ] UI displays correctly
  - [ ] Try sample contracts

- [ ] Check Lambda function in AWS Console
  - [ ] Function exists
  - [ ] Configuration is correct
  - [ ] No errors in CloudWatch Logs

- [ ] Test API endpoints (optional)
  ```bash
  curl -X GET $(terraform output -raw function_url)
  ```

- [ ] Review CloudWatch Logs
  ```bash
  aws logs tail $(terraform output -raw cloudwatch_log_group_name) --follow
  ```

## Production Deployment Checklist

### 🔒 Security Hardening

- [ ] Enable IAM authentication for Function URL
  ```hcl
  function_url_auth_type = "AWS_IAM"
  ```

- [ ] Restrict CORS origins
  ```hcl
  cors_allow_origins = ["https://yourdomain.com"]
  ```

- [ ] Enable CloudWatch alarms
  ```hcl
  enable_cloudwatch_alarms = true
  ```

- [ ] Configure remote state backend
  - [ ] Create S3 bucket for state
  - [ ] Create DynamoDB table for locking
  - [ ] Configure `backend.tf`
  - [ ] Migrate state: `terraform init -migrate-state`

- [ ] Review IAM permissions
  - [ ] Lambda execution role follows least privilege
  - [ ] Bedrock permissions are necessary
  - [ ] No overly broad permissions

### 📊 Monitoring Setup

- [ ] Configure CloudWatch Alarms
  - [ ] Error rate alarm
  - [ ] Duration alarm
  - [ ] Add SNS topic for notifications (optional)

- [ ] Set up CloudWatch Dashboard (optional)
  ```bash
  # Create custom dashboard in AWS Console
  ```

- [ ] Configure log retention
  ```hcl
  log_retention_days = 30  # Adjust as needed
  ```

### 💰 Cost Optimization

- [ ] Review Lambda configuration
  - [ ] Memory size appropriate for workload
  - [ ] Timeout not excessive
  - [ ] Architecture (x86_64 vs arm64)

- [ ] Set up cost alerts
  ```bash
  # AWS Console → Billing → Budgets
  ```

- [ ] Enable cost allocation tags
  ```hcl
  additional_tags = {
    CostCenter = "Legal-Tech"
    Project    = "Document-Analyzer"
  }
  ```

### 🔄 Backup and Recovery

- [ ] Enable S3 versioning for state bucket
  ```bash
  aws s3api put-bucket-versioning \
    --bucket my-terraform-state-bucket \
    --versioning-configuration Status=Enabled
  ```

- [ ] Document recovery procedures
  - [ ] State file recovery
  - [ ] Lambda function rollback
  - [ ] Configuration restore

- [ ] Test disaster recovery
  - [ ] Destroy and recreate in test environment
  - [ ] Verify state recovery works

## Maintenance Checklist

### 🔄 Regular Updates

- [ ] Update Lambda code
  ```bash
  # After updating lambda_function.py
  terraform apply -replace="aws_lambda_function.legal_analyzer"
  ```

- [ ] Update Terraform configuration
  ```bash
  terraform plan
  terraform apply
  ```

- [ ] Update providers
  ```bash
  terraform init -upgrade
  ```

### 📈 Monitoring

- [ ] Weekly: Review CloudWatch metrics
  - [ ] Invocation count
  - [ ] Error rate
  - [ ] Duration trends

- [ ] Monthly: Review costs
  - [ ] AWS Cost Explorer
  - [ ] Compare against budget

- [ ] Quarterly: Security review
  - [ ] IAM permissions audit
  - [ ] CORS configuration review
  - [ ] Update dependencies

## Troubleshooting Checklist

### ❌ Common Issues

- [ ] **Terraform init fails**
  - [ ] Check internet connectivity
  - [ ] Verify provider version constraints
  - [ ] Clear `.terraform` directory and retry

- [ ] **Plan shows unexpected changes**
  - [ ] Run `terraform refresh`
  - [ ] Check for manual changes in AWS Console
  - [ ] Review terraform.tfvars

- [ ] **Apply fails with permission error**
  - [ ] Verify AWS credentials
  - [ ] Check IAM permissions
  - [ ] Review error message for specific permission

- [ ] **Lambda function not working**
  - [ ] Check CloudWatch Logs
  - [ ] Verify Bedrock access enabled
  - [ ] Test Function URL
  - [ ] Review environment variables

- [ ] **State lock error**
  - [ ] Check DynamoDB table
  - [ ] Force unlock if safe: `terraform force-unlock LOCK_ID`
  - [ ] Verify no other operations in progress

## Cleanup Checklist

### 🗑️ Decommissioning

- [ ] Backup any important data
  - [ ] Export CloudWatch Logs
  - [ ] Save Terraform state

- [ ] Destroy infrastructure
  ```bash
  terraform plan -destroy
  terraform destroy
  ```

- [ ] Verify all resources deleted
  ```bash
  terraform state list
  ```

- [ ] Clean up state backend (if used)
  - [ ] Remove S3 state file
  - [ ] Delete DynamoDB lock table (optional)
  - [ ] Delete S3 bucket (optional)

- [ ] Remove local files
  ```bash
  rm -rf .terraform
  rm terraform.tfstate*
  ```

## Documentation Checklist

### 📚 Documentation

- [ ] Document deployment date and version
- [ ] Record Function URL
- [ ] Save configuration details
- [ ] Document any customizations
- [ ] Update team wiki/documentation
- [ ] Create runbook for operations team

## Sign-off

### Deployment Information

- **Deployed by:** _______________
- **Deployment date:** _______________
- **Environment:** ☐ Dev  ☐ Staging  ☐ Production
- **Terraform version:** _______________
- **AWS Region:** _______________
- **Function URL:** _______________

### Approvals

- [ ] Technical review completed
- [ ] Security review completed
- [ ] Cost review completed
- [ ] Documentation updated

---

**Checklist Version:** 1.0
**Last Updated:** 2025
**Next Review:** _______________
