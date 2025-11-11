# AWS Lambda Gen AI Dashboard - Deployment Guide

## Overview
This Lambda function hosts a web-based UI that displays:
- Current time (auto-updating)
- Weather for Houston, Texas
- Selection options for AWS Gen AI services

## Prerequisites
1. AWS Account
2. AWS CLI configured
3. OpenWeatherMap API key (free from https://openweathermap.org/api)

## Step-by-Step Deployment

### Step 1: Prepare the Deployment Package

1. Create a deployment directory:
```bash
mkdir lambda-deployment
cd lambda-deployment
```

2. Copy the lambda_function.py file to this directory

3. Install dependencies locally:
```bash
pip install -r requirements.txt -t .
```

4. Create a ZIP file:
```bash
zip -r lambda-function.zip .
```

### Step 2: Create the Lambda Function via AWS Console

1. **Go to AWS Lambda Console**
   - Navigate to https://console.aws.amazon.com/lambda/

2. **Create Function**
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `gen-ai-dashboard`
   - Runtime: Python 3.11 (or latest)
   - Architecture: x86_64
   - Click "Create function"

3. **Upload Code**
   - In the "Code" tab, click "Upload from" → ".zip file"
   - Upload your `lambda-function.zip`
   - Click "Save"

4. **Configure Environment Variables**
   - Go to "Configuration" → "Environment variables"
   - Click "Edit" → "Add environment variable"
   - Key: `OPENWEATHER_API_KEY`
   - Value: Your OpenWeatherMap API key
   - Click "Save"

5. **Adjust Settings**
   - Go to "Configuration" → "General configuration"
   - Click "Edit"
   - Memory: 256 MB
   - Timeout: 30 seconds
   - Click "Save"

### Step 3: Create API Gateway (Function URL - Easier Option)

**Option A: Lambda Function URL (Recommended for learning)**

1. In your Lambda function, go to "Configuration" → "Function URL"
2. Click "Create function URL"
3. Auth type: NONE (for public access)
4. CORS settings:
   - Allow origin: *
   - Allow methods: GET, POST
   - Allow headers: content-type
5. Click "Save"
6. Copy the Function URL - this is your web application URL!

**Option B: API Gateway (More features)**

1. Go to API Gateway console
2. Create new API → HTTP API
3. Add integration → Lambda
4. Select your function: `gen-ai-dashboard`
5. API name: `gen-ai-api`
6. Create routes:
   - GET /
   - POST /
7. Deploy
8. Copy the Invoke URL

### Step 4: Test Your Application

1. Open the Function URL or API Gateway URL in your browser
2. You should see:
   - Current time (updating every second)
   - Houston weather information
   - AWS Gen AI service cards
3. Click on a service card to select it
4. Click "Launch Selected Service" to test the POST functionality

### Step 5: Configure IAM Permissions (If using other AWS services)

If you plan to integrate with actual AWS Gen AI services, add these policies:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "comprehend:DetectSentiment",
                "rekognition:DetectLabels",
                "polly:SynthesizeSpeech",
                "lex:PostText",
                "sagemaker:InvokeEndpoint"
            ],
            "Resource": "*"
        }
    ]
}
```

## Alternative: Deploy Using AWS CLI

```bash
# Create the function
aws lambda create-function \
    --function-name gen-ai-dashboard \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --timeout 30 \
    --memory-size 256

# Set environment variable
aws lambda update-function-configuration \
    --function-name gen-ai-dashboard \
    --environment Variables={OPENWEATHER_API_KEY=your_api_key_here}

# Create function URL
aws lambda create-function-url-config \
    --function-name gen-ai-dashboard \
    --auth-type NONE \
    --cors AllowOrigins="*",AllowMethods="GET,POST",AllowHeaders="content-type"
```

## Project Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (User)        │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────────────────┐
│  Lambda Function URL or     │
│  API Gateway                │
└────────┬───────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  AWS Lambda Function        │
│  - Serves HTML UI           │
│  - Fetches weather data     │
│  - Handles service selection│
└────────┬───────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  External APIs              │
│  - OpenWeatherMap           │
│  - (Future: AWS Gen AI)     │
└─────────────────────────────┘
```

## Monitoring and Logs

1. View logs in CloudWatch:
   - Go to CloudWatch → Log groups
   - Find `/aws/lambda/gen-ai-dashboard`
   - Click to view execution logs

2. Monitor metrics:
   - Lambda console → Monitor tab
   - View invocations, duration, errors

## Cost Estimation

**Lambda:**
- First 1 million requests/month: FREE
- After that: $0.20 per 1 million requests
- Compute: $0.0000166667 per GB-second

**API Gateway/Function URL:**
- Function URL: FREE
- API Gateway: $1.00 per million requests (first tier)

**Expected monthly cost for learning:** < $1

## Troubleshooting

**Issue: Weather not displaying**
- Solution: Check if OPENWEATHER_API_KEY is set correctly
- Verify API key is valid at OpenWeatherMap

**Issue: Function timeout**
- Solution: Increase timeout in Lambda configuration
- Check CloudWatch logs for specific errors

**Issue: CORS errors**
- Solution: Ensure CORS is configured in Function URL or API Gateway
- Add proper headers in response

## Next Steps for Learning Gen AI

1. **Integrate Amazon Bedrock:**
   - Add a text input field
   - Send prompts to Claude via Bedrock API
   - Display AI responses

2. **Add Amazon Comprehend:**
   - Analyze sentiment of user input
   - Extract key phrases

3. **Implement Amazon Polly:**
   - Convert weather description to speech
   - Add audio playback

4. **Use Amazon Rekognition:**
   - Add image upload functionality
   - Detect objects in images

## Resources

- AWS Lambda Documentation: https://docs.aws.amazon.com/lambda/
- Amazon Bedrock: https://docs.aws.amazon.com/bedrock/
- OpenWeatherMap API: https://openweathermap.org/api
- AWS Gen AI Services: https://aws.amazon.com/ai/

## Security Notes

- For production, use API Gateway with authentication
- Never hardcode API keys in code
- Use AWS Secrets Manager for sensitive data
- Implement proper IAM roles with least privilege

## Support

For issues or questions:
- Check AWS Lambda documentation
- Review CloudWatch logs
- Verify IAM permissions
- Test with AWS CloudShell
