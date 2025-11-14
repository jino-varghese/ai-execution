# Legal Document Analysis Agent - Deployment Guide

This guide provides step-by-step instructions for deploying the Legal Document Review and Contract Analysis Agent to AWS.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Deployment (Recommended)](#quick-deployment-recommended)
- [Manual Deployment](#manual-deployment)
- [AWS Bedrock Setup](#aws-bedrock-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. AWS Account
- Sign up at https://aws.amazon.com if you don't have one
- Free tier eligible
- Credit card required (but won't be charged for normal usage)

### 2. AWS CLI Installation

**macOS:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows:**
Download installer from: https://aws.amazon.com/cli/

**Verify installation:**
```bash
aws --version
```

### 3. Configure AWS Credentials

```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security credentials
- **AWS Secret Access Key**: From the same location
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json`

### 4. AWS Bedrock Access

1. Go to AWS Console: https://console.aws.amazon.com
2. Navigate to **Amazon Bedrock** service
3. Click **Model access** in the left sidebar
4. Click **Manage model access**
5. Find **Anthropic Claude 3 Sonnet**
6. Click **Request model access**
7. Accept terms and submit
8. Wait for approval (usually instant)

## Quick Deployment (Recommended)

### Option 1: Automated Script

```bash
# 1. Clone or download the repository
cd legal-document-analyzer

# 2. Make scripts executable
chmod +x deploy.sh cleanup.sh

# 3. Run deployment
./deploy.sh
```

The script will:
- ✅ Verify AWS credentials
- ✅ Create IAM role with necessary permissions
- ✅ Package the Lambda function
- ✅ Deploy to AWS Lambda
- ✅ Create a public Function URL
- ✅ Display the access URL

**Expected output:**
```
==========================================
Deployment Complete!
==========================================

Legal Document Analysis Agent is live!

Access URL:
https://abc123xyz.lambda-url.us-east-1.on.aws/
```

### Option 2: AWS CloudShell (No Local Setup Required)

1. **Open AWS CloudShell**:
   - Go to AWS Console
   - Click the CloudShell icon (>_) in the top navigation bar

2. **Upload files**:
   ```bash
   # Create directory
   mkdir legal-analyzer
   cd legal-analyzer
   ```

3. **Upload via CloudShell**:
   - Click Actions → Upload file
   - Upload: `lambda_function.py`, `requirements.txt`, `deploy.sh`

4. **Deploy**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## Manual Deployment

If you prefer to deploy manually or understand each step:

### Step 1: Create IAM Role

1. Go to **IAM Console** → **Roles** → **Create role**
2. Select **Lambda** as the trusted entity
3. Click **Next**
4. Attach these policies:
   - `AWSLambdaBasicExecutionRole`
5. Click **Next** through tags
6. Name: `legal-document-analyzer-role`
7. Click **Create role**

### Step 2: Add Bedrock Permissions

1. Find the role you just created
2. Click **Add permissions** → **Create inline policy**
3. Switch to JSON and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

4. Name: `BedrockAccess`
5. Click **Create policy**

### Step 3: Create Lambda Function

1. Go to **Lambda Console** → **Create function**
2. Select **Author from scratch**
3. Function name: `legal-document-analyzer`
4. Runtime: **Python 3.11**
5. Architecture: **x86_64**
6. Execution role: **Use an existing role** → Select `legal-document-analyzer-role`
7. Click **Create function**

### Step 4: Upload Code

#### Option A: Direct Code Upload (Small files)

1. In the Lambda function page, scroll to **Code source**
2. Delete the default `lambda_function.py` content
3. Copy and paste the entire content from our `lambda_function.py`
4. Click **Deploy**

#### Option B: ZIP Upload (Recommended)

```bash
# Package the function
zip lambda-function.zip lambda_function.py

# Upload via AWS CLI
aws lambda update-function-code \
    --function-name legal-document-analyzer \
    --zip-file fileb://lambda-function.zip \
    --region us-east-1
```

### Step 5: Configure Lambda Settings

1. Go to **Configuration** tab
2. Click **General configuration** → **Edit**
3. Set:
   - **Memory**: 512 MB
   - **Timeout**: 1 minute
4. Click **Save**

### Step 6: Create Function URL

1. Go to **Configuration** tab → **Function URL**
2. Click **Create function URL**
3. Set:
   - **Auth type**: NONE
   - **Configure cross-origin resource sharing (CORS)**: ✅ Checked
     - Allow origin: `*`
     - Allow methods: `GET, POST`
     - Allow headers: `content-type`
4. Click **Save**
5. **Copy the Function URL** - this is your application URL!

## AWS Bedrock Setup

### Verify Bedrock Access

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1 | grep -i claude

# Or in Python
import boto3
bedrock = boto3.client('bedrock', region_name='us-east-1')
models = bedrock.list_foundation_models()
for model in models['modelSummaries']:
    if 'claude' in model['modelId'].lower():
        print(model['modelId'])
```

### Request Model Access (If Needed)

If you get "AccessDeniedException":

1. AWS Console → Bedrock → Model access
2. Click **Manage model access**
3. Enable: **Anthropic Claude 3 Sonnet**
4. Submit request
5. Wait for approval email (usually < 5 minutes)

## Verification

### 1. Test via Web Browser

1. Open the Function URL in your browser
2. You should see the Legal Document Analysis interface
3. Try loading a sample contract (NDA, Service Agreement)
4. Click **Analyze Document**
5. Verify you receive analysis results

### 2. Test via API (Optional)

```bash
# GET request - should return HTML UI
curl https://YOUR-FUNCTION-URL.lambda-url.us-east-1.on.aws/

# POST request - analyze document
curl -X POST https://YOUR-FUNCTION-URL.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{
    "document": "This Service Agreement is entered into between Provider and Client. Provider shall indemnify Client for all claims.",
    "type": "contract"
  }'
```

### 3. Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/legal-document-analyzer --follow --region us-east-1

# Or in AWS Console:
# CloudWatch → Log Groups → /aws/lambda/legal-document-analyzer
```

## Troubleshooting

### Issue: "AccessDeniedException" from Bedrock

**Solution:**
1. Verify model access is enabled
2. Check IAM role has `bedrock:InvokeModel` permission
3. Ensure correct model ID: `anthropic.claude-3-sonnet-20240229-v1:0`

```bash
# Check IAM permissions
aws iam get-role-policy \
    --role-name legal-document-analyzer-role \
    --policy-name BedrockAccess
```

### Issue: Function Times Out

**Solution:**
```bash
# Increase timeout
aws lambda update-function-configuration \
    --function-name legal-document-analyzer \
    --timeout 120 \
    --region us-east-1
```

### Issue: Memory Exceeded

**Solution:**
```bash
# Increase memory
aws lambda update-function-configuration \
    --function-name legal-document-analyzer \
    --memory-size 1024 \
    --region us-east-1
```

### Issue: CORS Errors

**Solution:**
```bash
# Update CORS config
aws lambda update-function-url-config \
    --function-name legal-document-analyzer \
    --cors '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST"],
        "AllowHeaders": ["content-type"]
    }' \
    --region us-east-1
```

## Next Steps

After successful deployment:

1. **Test with Real Contracts**: Upload your own legal documents
2. **Monitor Costs**: Check AWS Cost Explorer
3. **Review Logs**: Ensure no errors in CloudWatch
4. **Customize**: Modify risk detection patterns
5. **Enhance**: Add more features from the roadmap

---

**Deployment Guide for Legal Document Analysis Agent**

*Built with AWS Lambda + Bedrock Claude AI*
