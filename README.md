# 🚀 AWS Gen AI Dashboard - Houston Weather App

A serverless web application built with AWS Lambda that displays real-time Houston weather and provides interactive AWS Gen AI service selection. Perfect for learning AWS serverless architecture and Gen AI services!

## ✨ Features

- **Real-Time Weather**: Live Houston, Texas weather data (temperature, conditions, humidity)
- **Auto-Updating Clock**: Current time that updates every second
- **Interactive Service Selection**: Click to explore 6 AWS Gen AI services:
  - Amazon Bedrock (Foundation Models)
  - Amazon SageMaker (ML Training & Deployment)
  - Amazon Comprehend (NLP & Text Analytics)
  - Amazon Lex (Conversational AI)
  - Amazon Polly (Text-to-Speech)
  - Amazon Rekognition (Image & Video Analysis)
- **Responsive Design**: Beautiful gradient UI that works on all devices
- **Serverless Architecture**: No servers to manage!

## 🏗️ Architecture

```
User Browser
     ↓
Lambda Function URL
     ↓
AWS Lambda (Python)
     ↓
External APIs (Weather)
```

## 📋 Prerequisites

1. **AWS Account** (Free tier eligible)
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **OpenWeatherMap API Key** (Free from https://openweathermap.org/api)
4. **Python 3.11** or later

## 🚀 Quick Start (Automated Deployment)

### Option 1: One-Command Deployment

```bash
# Clone or download the files
cd aws-genai-dashboard

# Run the deployment script
./deploy.sh
```

The script will:
1. ✅ Verify AWS credentials
2. ✅ Create IAM role (if needed)
3. ✅ Package dependencies
4. ✅ Deploy Lambda function
5. ✅ Create public Function URL
6. ✅ Configure environment variables

**You'll get a URL like:** `https://abc123xyz.lambda-url.us-east-1.on.aws/`

### Option 2: Manual Deployment (AWS Console)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed step-by-step instructions.

## 🧪 Testing Your Application

1. Open the Function URL in your browser
2. You should see:
   - ✅ Current time (auto-updating)
   - ✅ Houston weather (temp, conditions, humidity)
   - ✅ 6 Gen AI service cards
3. Click on any service card to select it
4. Click "Launch Selected Service" button
5. See the response with service details

## 📁 Project Structure

```
aws-genai-dashboard/
├── lambda_function.py      # Main Lambda handler with UI
├── requirements.txt        # Python dependencies
├── deploy.sh              # Automated deployment script
├── cleanup.sh             # Resource cleanup script
├── DEPLOYMENT_GUIDE.md    # Detailed deployment instructions
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Set in AWS Lambda Configuration → Environment Variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap API key | Yes |

### Getting OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Navigate to API Keys section
4. Copy your API key
5. Use it during deployment or add manually in Lambda console

## 💰 Cost Estimate

**Monthly cost for learning:** < $1

- **Lambda**: First 1M requests FREE, then $0.20/million
- **Function URL**: FREE (no API Gateway charges)
- **Data Transfer**: First 1 GB FREE
- **OpenWeatherMap API**: FREE tier (60 calls/minute)

## 📊 Monitoring & Logs

View logs in real-time:
```bash
aws logs tail /aws/lambda/gen-ai-dashboard --follow
```

Or check in AWS Console:
- CloudWatch → Log Groups → `/aws/lambda/gen-ai-dashboard`

## 🛠️ Customization Ideas

### 1. Change Location
Edit in `lambda_function.py`:
```python
# Change these coordinates
lat = 29.7604  # Houston
lon = -95.3698
```

### 2. Add More Services
Add new service cards in the `get_html_page()` function:
```html
<div class="service-card" data-service="translate" onclick="selectService(this)">
    <h3>🌐 Amazon Translate</h3>
    <p>Real-time language translation</p>
</div>
```

### 3. Integrate Real Gen AI Services

Example: Add Amazon Bedrock integration:

```python
import boto3
bedrock = boto3.client('bedrock-runtime')

def call_bedrock(prompt):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        })
    )
    return json.loads(response['body'].read())
```

## 🧹 Cleanup

Remove all AWS resources:
```bash
./cleanup.sh
```

This will delete:
- Lambda function
- IAM role
- Function URL configuration

## 🔒 Security Best Practices

### Current Setup (Learning/Demo)
- ✅ Public Function URL (easy testing)
- ✅ Environment variables for secrets
- ✅ No hardcoded credentials

### For Production
- 🔐 Add API Gateway with authentication
- 🔐 Use AWS Secrets Manager
- 🔐 Implement rate limiting
- 🔐 Add CloudFront for DDoS protection
- 🔐 Enable CloudWatch alarms
- 🔐 Use private VPC for sensitive data

## 📚 Learning Resources

### AWS Documentation
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
- [AWS Gen AI Services](https://aws.amazon.com/ai/)

### Next Learning Steps
1. **Add Bedrock Integration**: Make actual AI calls
2. **Implement DynamoDB**: Store user selections
3. **Add S3 Storage**: Upload and analyze images
4. **Create Step Functions**: Orchestrate multiple services
5. **Build Chatbot**: Use Amazon Lex

## 🐛 Troubleshooting

### Weather Not Showing
```bash
# Check if API key is set
aws lambda get-function-configuration \
    --function-name gen-ai-dashboard \
    --query Environment.Variables
```

### Function Timeout
```bash
# Increase timeout to 30 seconds
aws lambda update-function-configuration \
    --function-name gen-ai-dashboard \
    --timeout 30
```

### CORS Errors
Make sure Function URL has CORS configured:
```bash
aws lambda update-function-url-config \
    --function-name gen-ai-dashboard \
    --cors AllowOrigins="*",AllowMethods="GET,POST",AllowHeaders="content-type"
```

## 🤝 Contributing

This is a learning project! Feel free to:
- Add more features
- Improve the UI
- Integrate more AWS services
- Create tutorials

## 📝 License

MIT License - Feel free to use for learning and projects!

## 🎯 What You'll Learn

By deploying this project, you'll gain hands-on experience with:

1. **AWS Lambda**: Serverless functions, handlers, environment variables
2. **Lambda Function URLs**: Public endpoints without API Gateway
3. **IAM Roles**: Permissions and execution roles
4. **CloudWatch**: Logging and monitoring
5. **Python Web Development**: HTML/CSS/JavaScript in Lambda
6. **External API Integration**: OpenWeatherMap API
7. **AWS CLI**: Command-line deployment and management
8. **Serverless Architecture**: Benefits and best practices

## 🚀 What's Next?

After mastering this dashboard:

1. **Add Real AI Features**:
   - Text generation with Bedrock
   - Sentiment analysis with Comprehend
   - Image recognition with Rekognition

2. **Build a Full Application**:
   - User authentication (Cognito)
   - Data persistence (DynamoDB)
   - File storage (S3)
   - Email notifications (SES)

3. **Advanced Topics**:
   - Infrastructure as Code (CloudFormation/CDK)
   - CI/CD pipelines (CodePipeline)
   - Multi-region deployment
   - Auto-scaling strategies

## 📧 Questions?

- Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions
- Review AWS Lambda documentation
- Check CloudWatch logs for errors
- Test with AWS CloudShell

---

**Happy Learning! 🎓**

Built with ❤️ for learning AWS Gen AI
