import boto3
import json
import os
from botocore.exceptions import ClientError

SOURCE_BUCKET = "scg-gyyaf-prd-wus2-s3-ccm-com-curated"
SOURCE_KEY = "training/parquet_byzip/90012.parquet"

DEST_BUCKET = "scg-gyyaf-wus2-s3-ccm-fargate-zip-com-container"
DEST_KEY = "test_queries/90012.parquet"  # will create test_queries/ prefix

# Secret name in AWS Secrets Manager
SECRET_NAME = "scg-gyyaf-prd-wus2-iam-user-s3-access-key-rotate-secret"


def get_secret_credentials(secret_name, region_name=None):
    """
    Retrieve IAM user credentials from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret in Secrets Manager
        region_name: AWS region (optional, uses Lambda's region if not specified)

    Returns:
        dict: Contains 'AccessKeyId' and 'SecretAccessKey'

    Raises:
        ValueError: If secret is not found or malformed
        ClientError: If Secrets Manager operation fails
    """
    # Create Secrets Manager client
    # If region_name is not provided, it will use the Lambda's region
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name or os.environ.get('AWS_REGION', 'us-west-2')
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            raise ValueError(f"Secret '{secret_name}' not found in Secrets Manager")
        elif error_code == 'InvalidRequestException':
            raise ValueError(f"Invalid request for secret '{secret_name}'")
        elif error_code == 'InvalidParameterException':
            raise ValueError(f"Invalid parameter for secret '{secret_name}'")
        elif error_code == 'DecryptionFailure':
            raise ValueError(f"Cannot decrypt secret '{secret_name}'")
        elif error_code == 'InternalServiceError':
            raise ValueError(f"Internal service error retrieving secret '{secret_name}'")
        else:
            raise

    # Parse the secret string (should be JSON)
    try:
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
        else:
            raise ValueError(f"Secret '{secret_name}' does not contain SecretString")

        # Validate required keys
        if 'AccessKeyId' not in secret or 'SecretAccessKey' not in secret:
            raise ValueError(
                f"Secret '{secret_name}' missing required keys. "
                "Expected 'AccessKeyId' and 'SecretAccessKey'"
            )

        return {
            'AccessKeyId': secret['AccessKeyId'],
            'SecretAccessKey': secret['SecretAccessKey']
        }

    except json.JSONDecodeError as e:
        raise ValueError(f"Secret '{secret_name}' is not valid JSON: {e}")


def lambda_handler(event, context):
    """
    Copies one object from prod S3 to dev S3.
    - Read from prod using Lambda execution role
    - Write to dev using IAM user credentials from Secrets Manager

    The Lambda execution role must have:
      1. s3:GetObject permission on source bucket
      2. secretsmanager:GetSecretValue permission on the secret

    The IAM user (credentials from secret) must have:
      1. s3:PutObject permission on destination bucket

    Optional event parameters:
      - secret_name: Override default SECRET_NAME
      - region_name: Override AWS region for Secrets Manager
      - source_bucket: Override SOURCE_BUCKET
      - source_key: Override SOURCE_KEY
      - dest_bucket: Override DEST_BUCKET
      - dest_key: Override DEST_KEY
    """

    # Allow override of configuration via event
    secret_name = event.get('secret_name', SECRET_NAME) if isinstance(event, dict) else SECRET_NAME
    region_name = event.get('region_name') if isinstance(event, dict) else None

    source_bucket = event.get('source_bucket', SOURCE_BUCKET) if isinstance(event, dict) else SOURCE_BUCKET
    source_key = event.get('source_key', SOURCE_KEY) if isinstance(event, dict) else SOURCE_KEY
    dest_bucket = event.get('dest_bucket', DEST_BUCKET) if isinstance(event, dict) else DEST_BUCKET
    dest_key = event.get('dest_key', DEST_KEY) if isinstance(event, dict) else DEST_KEY

    print(f"Starting S3 copy operation...")
    print(f"Source: s3://{source_bucket}/{source_key}")
    print(f"Destination: s3://{dest_bucket}/{dest_key}")

    # 1. Retrieve IAM user credentials from Secrets Manager
    try:
        print(f"Retrieving credentials from Secrets Manager: {secret_name}")
        credentials = get_secret_credentials(secret_name, region_name)
        print("Successfully retrieved credentials from Secrets Manager")
    except Exception as e:
        print(f"Error retrieving credentials from Secrets Manager: {e}")
        raise

    # 2. S3 client for prod (uses Lambda execution role)
    s3_prod = boto3.client("s3")

    # 3. S3 client for dev (uses IAM user credentials from Secrets Manager)
    s3_dev = boto3.client(
        "s3",
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
    )

    # 4. Read object from prod
    try:
        print(f"Reading object from source bucket: {source_bucket}/{source_key}")
        response = s3_prod.get_object(Bucket=source_bucket, Key=source_key)
        body_stream = response["Body"]
        content_length = response.get('ContentLength', 'unknown')
        print(f"Successfully read object (size: {content_length} bytes)")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Error reading from prod bucket: {error_code} - {e}")
        raise
    except Exception as e:
        print(f"Unexpected error reading from prod bucket: {e}")
        raise

    # 5. Write object to dev
    try:
        print(f"Writing object to destination bucket: {dest_bucket}/{dest_key}")
        s3_dev.upload_fileobj(
            Fileobj=body_stream,
            Bucket=dest_bucket,
            Key=dest_key,
        )
        print("Successfully wrote object to destination bucket")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Error writing to dev bucket: {error_code} - {e}")
        raise
    except Exception as e:
        print(f"Unexpected error writing to dev bucket: {e}")
        raise

    result = {
        "status": "success",
        "source": f"s3://{source_bucket}/{source_key}",
        "destination": f"s3://{dest_bucket}/{dest_key}",
        "message": "Object copied successfully"
    }

    print(f"Copy operation completed successfully")
    return result


# For local testing
if __name__ == "__main__":
    # Test the lambda handler
    test_event = {}
    test_context = {}

    try:
        result = lambda_handler(test_event, test_context)
        print("\nTest Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nTest Failed: {e}")
