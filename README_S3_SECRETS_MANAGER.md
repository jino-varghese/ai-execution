# S3 Copy Lambda with AWS Secrets Manager Integration

## Overview

This Lambda function copies S3 objects from a production bucket to a development/container bucket using IAM user credentials stored securely in AWS Secrets Manager.

## Key Improvements

### 1. **Security Enhancement**
- ✅ Credentials stored in AWS Secrets Manager (not in code or environment variables)
- ✅ Automatic credential rotation support
- ✅ Centralized secret management
- ✅ No hardcoded credentials

### 2. **Better Error Handling**
- Specific error messages for different failure scenarios
- Detailed logging for troubleshooting
- Proper exception handling for Secrets Manager operations

### 3. **Flexibility**
- Support for runtime configuration via event parameters
- Override defaults for buckets, keys, and secret names
- Local testing support

## Architecture

```
┌─────────────┐
│   Lambda    │
│  Function   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────────┐
│   Secrets   │   │   S3 Buckets    │
│   Manager   │   │                 │
│             │   │ • Source (prod) │
│  Secret:    │   │ • Dest (dev)    │
│  AccessKey  │   └─────────────────┘
│  SecretKey  │
└─────────────┘
```

## Prerequisites

### 1. AWS Secrets Manager Secret

Create a secret in AWS Secrets Manager with the following structure:

**Secret Name:** `scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret`

**Secret Value (JSON):**
```json
{
  "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

#### Creating the Secret via AWS CLI:
```bash
aws secretsmanager create-secret \
    --name scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret \
    --description "IAM user credentials for S3 cross-account access" \
    --secret-string '{"AccessKeyId":"YOUR_ACCESS_KEY","SecretAccessKey":"YOUR_SECRET_KEY"}' \
    --region us-west-2
```

#### Creating the Secret via AWS Console:
1. Go to AWS Secrets Manager
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Choose "Plaintext" and enter:
   ```json
   {
     "AccessKeyId": "YOUR_ACCESS_KEY",
     "SecretAccessKey": "YOUR_SECRET_KEY"
   }
   ```
5. Name it: `scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret`
6. Click "Store"

### 2. IAM Permissions

#### Lambda Execution Role Requirements:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::scg-gyyaf-prd-wus2-s3-ccm-com-curated/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-west-2:*:secret:scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### IAM User (from Secret) Requirements:
The IAM user whose credentials are stored in Secrets Manager needs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::scg-gyyaf-wus2-s3-ccm-fargate-zip-com-container/*"
    }
  ]
}
```

## Configuration

### Default Configuration
The following defaults are set in the code:

| Parameter | Default Value |
|-----------|--------------|
| Source Bucket | `scg-gyyaf-prd-wus2-s3-ccm-com-curated` |
| Source Key | `training/parquet_byzip/90012.parquet` |
| Destination Bucket | `scg-gyyaf-wus2-s3-ccm-fargate-zip-com-container` |
| Destination Key | `test_queries/90012.parquet` |
| Secret Name | `scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret` |

### Runtime Overrides
You can override defaults by passing event parameters:

```json
{
  "source_bucket": "my-custom-source-bucket",
  "source_key": "path/to/file.parquet",
  "dest_bucket": "my-custom-dest-bucket",
  "dest_key": "new/path/file.parquet",
  "secret_name": "my-custom-secret-name",
  "region_name": "us-east-1"
}
```

## Usage

### Lambda Invocation

#### Example 1: Use defaults
```python
import boto3
import json

lambda_client = boto3.client('lambda')

response = lambda_client.invoke(
    FunctionName='your-lambda-function-name',
    InvocationType='RequestResponse',
    Payload=json.dumps({})
)

result = json.loads(response['Payload'].read())
print(result)
```

#### Example 2: Override source/destination
```python
response = lambda_client.invoke(
    FunctionName='your-lambda-function-name',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'source_key': 'training/parquet_byzip/90013.parquet',
        'dest_key': 'test_queries/90013.parquet'
    })
)
```

### Expected Response
```json
{
  "status": "success",
  "source": "s3://scg-gyyaf-prd-wus2-s3-ccm-com-curated/training/parquet_byzip/90012.parquet",
  "destination": "s3://scg-gyyaf-wus2-s3-ccm-fargate-zip-com-container/test_queries/90012.parquet",
  "message": "Object copied successfully"
}
```

## Error Handling

The function provides detailed error messages for common scenarios:

### Secret Not Found
```
ValueError: Secret 'scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret' not found in Secrets Manager
```

### Malformed Secret
```
ValueError: Secret 'scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret' missing required keys. Expected 'AccessKeyId' and 'SecretAccessKey'
```

### S3 Access Denied
```
Error reading from prod bucket: AccessDenied - An error occurred (AccessDenied) when calling the GetObject operation
```

## Local Testing

For local testing, ensure you have AWS credentials configured:

```bash
export AWS_PROFILE=your-profile
python lambda_s3_copy_with_secrets_manager.py
```

## Deployment

### 1. Package the Lambda
```bash
zip lambda_function.zip lambda_s3_copy_with_secrets_manager.py
```

### 2. Create/Update Lambda Function
```bash
aws lambda create-function \
    --function-name s3-copy-with-secrets \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
    --handler lambda_s3_copy_with_secrets_manager.lambda_handler \
    --zip-file fileb://lambda_function.zip \
    --timeout 60 \
    --memory-size 256
```

Or update existing:
```bash
aws lambda update-function-code \
    --function-name s3-copy-with-secrets \
    --zip-file fileb://lambda_function.zip
```

## Monitoring

Monitor the function using CloudWatch Logs:
```bash
aws logs tail /aws/lambda/s3-copy-with-secrets --follow
```

## Security Best Practices

1. ✅ **Use Secrets Manager** for credential storage
2. ✅ **Enable automatic rotation** for IAM user credentials
3. ✅ **Use least privilege** IAM policies
4. ✅ **Enable CloudTrail** to audit secret access
5. ✅ **Use VPC endpoints** for Secrets Manager (if Lambda is in VPC)
6. ✅ **Encrypt secrets** using KMS (enabled by default)

## Credential Rotation

To enable automatic rotation:

```bash
aws secretsmanager rotate-secret \
    --secret-id scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret \
    --rotation-lambda-arn arn:aws:lambda:us-west-2:YOUR_ACCOUNT:function:SecretsManagerRotation \
    --rotation-rules AutomaticallyAfterDays=30
```

## Comparison: Old vs New

| Feature | Old Version | New Version |
|---------|-------------|-------------|
| Credential Storage | Event/Environment Variables | AWS Secrets Manager |
| Security | ⚠️ Credentials in plain text | ✅ Encrypted at rest |
| Rotation Support | ❌ Manual | ✅ Automatic |
| Auditability | ❌ Limited | ✅ CloudTrail integration |
| Error Handling | Basic | Comprehensive |
| Flexibility | Limited | Event-based overrides |
| Logging | Minimal | Detailed |

## Troubleshooting

### Issue: "Secret not found"
- Verify secret exists: `aws secretsmanager describe-secret --secret-id SECRET_NAME`
- Check region matches Lambda region

### Issue: "Access Denied" on Secrets Manager
- Verify Lambda execution role has `secretsmanager:GetSecretValue` permission
- Check resource ARN in policy matches secret ARN

### Issue: "Access Denied" on S3
- Verify Lambda role has `s3:GetObject` on source bucket
- Verify IAM user (from secret) has `s3:PutObject` on destination bucket

## License

Internal use only - Southern California Gas Company
