# 🚀 AWS Gen AI Dashboard

A serverless web application built with AWS Lambda that displays real-time weather data for multiple US cities and provides interactive AWS Gen AI service selection. Perfect for learning AWS serverless architecture and Gen AI services!

## ✨ Features

- **Real-Time Weather**: Live weather data for 10 major US cities (temperature, conditions, humidity)
- **Multi-City Support**: Dropdown selector for Houston, New York, Los Angeles, Chicago, Miami, Seattle, Boston, San Francisco, Austin, and Denver
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
AWS Lambda (Python 3.11)
     ↓
OpenWeatherMap API
```

**AWS Resources:**
- AWS Lambda Function
- Lambda Function URL (no API Gateway needed)
- IAM Role with basic execution permissions
- CloudWatch Log Group

## 📋 Prerequisites

1. **AWS Account** (Free tier eligible)
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **OpenWeatherMap API Key** (Free from https://openweathermap.org/api)
4. **Python 3.11** or later

### Additional Prerequisites for Terraform

5. **Terraform** 1.0 or later (Download from https://www.terraform.io/downloads)
6. **pip** (Python package installer)

## 🚀 Deployment Options

Choose your preferred deployment method:

### Option 1: Bash Script Deployment (Quick & Easy)

Perfect for quick deployment and testing.

#### Steps:

1. **Get OpenWeatherMap API Key**
   - Visit https://openweathermap.org/api
   - Sign up for a free account
   - Copy your API key

2. **Run Deployment Script**
   ```bash
   ./deploy.sh
   ```

3. **Enter API Key**
   - The script will prompt for your OpenWeatherMap API key
   - Paste it when requested

4. **Access Your App**
   - The script will display your Function URL
   - Open it in your browser

#### What the Script Does:

✅ Verifies AWS credentials
✅ Creates IAM role (if needed)
✅ Packages dependencies
✅ Deploys Lambda function
✅ Creates public Function URL
✅ Configures environment variables

---

### Option 2: Terraform Deployment (Infrastructure as Code)

Perfect for production deployments and team collaboration.

#### Steps:

1. **Get OpenWeatherMap API Key**
   - Visit https://openweathermap.org/api
   - Sign up for a free account
   - Copy your API key

2. **Run Terraform Deployment Script**
   ```bash
   ./deploy-terraform.sh
   ```

   Or manually:

   ```bash
   # Create terraform.tfvars from example
   cp terraform.tfvars.example terraform.tfvars

   # Edit terraform.tfvars and add your API key
   nano terraform.tfvars

   # Initialize Terraform
   terraform init

   # Review deployment plan
   terraform plan

   # Apply configuration
   terraform apply
   ```

3. **Access Your App**
   - Terraform will output your Function URL
   - Open it in your browser

#### Terraform Advantages:

✅ Infrastructure as Code (IaC)
✅ Version control for infrastructure
✅ Easy updates and rollbacks
✅ State management
✅ Team collaboration
✅ Repeatable deployments

#### Terraform Files:

- `main.tf` - Main infrastructure configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values (Function URL, etc.)
- `terraform.tfvars.example` - Example variables file
- `deploy-terraform.sh` - Automated deployment script

---

## 📁 Project Structure

```
aws-genai-dashboard/
├── lambda_function.py          # Main Lambda handler with UI
├── requirements.txt            # Python dependencies
│
├── deploy.sh                   # Bash deployment script
├── cleanup.sh                  # Bash cleanup script
│
├── main.tf                     # Terraform main configuration
├── variables.tf                # Terraform variables
├── outputs.tf                  # Terraform outputs
├── terraform.tfvars.example    # Terraform variables template
├── deploy-terraform.sh         # Terraform deployment script
│
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🧪 Testing Your Application

1. Open the Function URL in your browser
2. You should see:
   - ✅ Current time (auto-updating)
   - ✅ Weather data for selected city
   - ✅ City dropdown selector
   - ✅ 6 Gen AI service cards
3. Select a different city from the dropdown
4. Watch the weather update automatically
5. Click on any service card to select it
6. Click "Launch Selected Service" button
7. See the response with service details

## 🔧 Configuration

### Environment Variables

Set in AWS Lambda Configuration → Environment Variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHER_API_KEY` | Your OpenWeatherMap API key | Yes |

### Customization

#### Change Cities

Edit the `CITIES` dictionary in `lambda_function.py:11-22`:

```python
CITIES = {
    'yourcity': {'name': 'Your City, ST', 'lat': 00.0000, 'lon': -00.0000},
    # Add more cities...
}
```

#### Change Colors

Modify the CSS gradient in `lambda_function.py:151`:

```python
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 💰 Cost Estimate

**Monthly cost for learning:** < $1

- **Lambda**: First 1M requests FREE, then $0.20/million
- **Function URL**: FREE (no API Gateway charges)
- **CloudWatch Logs**: First 5GB FREE
- **Data Transfer**: First 1 GB FREE
- **OpenWeatherMap API**: FREE tier (60 calls/minute)

## 📊 Monitoring & Logs

### View Real-time Logs

```bash
aws logs tail /aws/lambda/gen-ai-dashboard --follow
```

### CloudWatch Console

AWS Console → CloudWatch → Log Groups → `/aws/lambda/gen-ai-dashboard`

### Terraform Outputs

View all deployment outputs:
```bash
terraform output
```

Get specific output:
```bash
terraform output function_url
```

## 🛠️ Management Commands

### Bash Script Method

**View logs:**
```bash
aws logs tail /aws/lambda/gen-ai-dashboard --follow
```

**Update function:**
```bash
./deploy.sh  # Will update existing function
```

**Delete resources:**
```bash
./cleanup.sh
```

### Terraform Method

**View deployment info:**
```bash
terraform output
```

**Update infrastructure:**
```bash
terraform apply
```

**View planned changes:**
```bash
terraform plan
```

**Destroy all resources:**
```bash
terraform destroy
```

**View current state:**
```bash
terraform show
```

## 🔒 Security Best Practices

### Current Setup (Learning/Demo)
- ✅ Public Function URL (easy testing)
- ✅ Environment variables for secrets
- ✅ No hardcoded credentials
- ✅ IAM role with minimal permissions
- ✅ CloudWatch logging enabled

### For Production
- 🔐 Add API Gateway with authentication
- 🔐 Use AWS Secrets Manager for API keys
- 🔐 Implement rate limiting
- 🔐 Add CloudFront for DDoS protection
- 🔐 Enable CloudWatch alarms
- 🔐 Use private VPC for sensitive data
- 🔐 Enable AWS WAF

## 🐛 Troubleshooting

### Weather Not Showing

**Check if API key is set:**
```bash
aws lambda get-function-configuration \
    --function-name gen-ai-dashboard \
    --query Environment.Variables
```

**Update API key:**
```bash
aws lambda update-function-configuration \
    --function-name gen-ai-dashboard \
    --environment "Variables={OPENWEATHER_API_KEY=your_key_here}"
```

Or with Terraform:
```bash
# Edit terraform.tfvars and run:
terraform apply
```

### Function Timeout

**Increase timeout:**
```bash
aws lambda update-function-configuration \
    --function-name gen-ai-dashboard \
    --timeout 30
```

Or edit `variables.tf` and run `terraform apply`

### Terraform State Issues

**Reset state (use with caution):**
```bash
terraform state list
terraform state rm <resource>  # Remove specific resource
```

**Import existing resources:**
```bash
terraform import aws_lambda_function.gen_ai_dashboard gen-ai-dashboard
```

### Permission Errors

**Verify AWS credentials:**
```bash
aws sts get-caller-identity
```

**Check IAM permissions:**
- Lambda full access
- IAM role creation
- CloudWatch Logs

## 📚 Learning Resources

### AWS Documentation
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
- [AWS Gen AI Services](https://aws.amazon.com/ai/)

### Terraform Documentation
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Lambda Resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function)

### Next Learning Steps
1. **Add Bedrock Integration**: Make actual AI calls
2. **Implement DynamoDB**: Store user selections
3. **Add S3 Storage**: Upload and analyze images
4. **Create Step Functions**: Orchestrate multiple services
5. **Build Chatbot**: Use Amazon Lex

## 🎯 What You'll Learn

By deploying this project, you'll gain hands-on experience with:

### AWS Services
1. **AWS Lambda**: Serverless functions, handlers, environment variables
2. **Lambda Function URLs**: Public endpoints without API Gateway
3. **IAM Roles**: Permissions and execution roles
4. **CloudWatch**: Logging and monitoring

### Development Tools
5. **Python Web Development**: HTML/CSS/JavaScript in Lambda
6. **External API Integration**: OpenWeatherMap API
7. **AWS CLI**: Command-line deployment and management
8. **Terraform**: Infrastructure as Code (IaC)

### DevOps Practices
9. **Serverless Architecture**: Benefits and best practices
10. **Infrastructure as Code**: Terraform workflows
11. **Version Control**: Git for code and infrastructure
12. **Deployment Automation**: Bash and Terraform scripts

## 🔄 Comparison: Bash vs Terraform

| Feature | Bash Script | Terraform |
|---------|-------------|-----------|
| **Deployment Speed** | ⚡ Fast (1-2 min) | 🐢 Moderate (2-3 min) |
| **Learning Curve** | ✅ Easy | 📚 Moderate |
| **State Management** | ❌ None | ✅ Built-in |
| **Team Collaboration** | ❌ Limited | ✅ Excellent |
| **Infrastructure Versioning** | ❌ Manual | ✅ Automatic |
| **Rollback** | ❌ Manual | ✅ Easy |
| **Multi-Environment** | ❌ Complex | ✅ Simple |
| **Best For** | Quick tests, learning | Production, teams |

## 🤝 Contributing

This is a learning project! Feel free to:
- Add more features
- Improve the UI
- Integrate more AWS services
- Create tutorials
- Submit pull requests

## 📝 License

MIT License - Feel free to use for learning and projects!

## 🎓 Next Steps

After mastering this dashboard:

### Week 1: Explore
- Deploy using both methods
- Test all features
- Explore CloudWatch logs
- Understand the code

### Week 2: Customize
- Add new cities
- Change UI colors
- Modify service descriptions
- Add new Gen AI services

### Week 3: Enhance
- Integrate Amazon Bedrock for text generation
- Add sentiment analysis with Comprehend
- Implement image recognition with Rekognition
- Use Polly to speak the weather

### Week 4: Scale
- Add DynamoDB for data persistence
- Implement user authentication with Cognito
- Add API Gateway with rate limiting
- Deploy multi-region setup

---

**Happy Learning! 🎓**

Built with ❤️ for learning AWS Gen AI

---

## 📞 Support

- **Issues**: Check CloudWatch logs first
- **AWS Documentation**: https://docs.aws.amazon.com/
- **Community**: AWS Forums, Stack Overflow (tag: `aws-lambda`)
- **Terraform**: https://www.terraform.io/docs/

## 🔗 Quick Links

- [OpenWeatherMap API](https://openweathermap.org/api)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Terraform Downloads](https://www.terraform.io/downloads)
- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
