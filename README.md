# AI-Powered Travel Itinerary Generator

A simple yet powerful web application that generates personalized travel itineraries using AI, deployed on AWS with Terraform.

## Overview

This project demonstrates a Tourism and Hospitality AI solution that creates custom travel itineraries based on:
- User preferences (destination, duration, budget)
- Travel interests (culture, food, adventure, nature, shopping, relaxation)
- Travel style (solo, couple, family, group)

### Key Features

- **Simple Web Interface**: Clean, responsive UI for inputting travel preferences
- **AI-Powered Generation**: Smart itinerary creation based on destination data and user preferences
- **Serverless Architecture**: Cost-effective AWS Lambda backend
- **Static Website Hosting**: Fast S3-based frontend delivery
- **RESTful API**: API Gateway for seamless frontend-backend communication
- **Infrastructure as Code**: Complete Terraform deployment scripts

### Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python 3.11 (AWS Lambda)
- **Infrastructure**: AWS (S3, Lambda, API Gateway, CloudWatch)
- **IaC**: Terraform
- **No Docker, No RDS**: Keeping it simple as requested

## Project Structure

```
.
├── frontend/                 # Static website files
│   ├── index.html           # Main HTML page
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       └── app.js           # Frontend logic
├── backend/                  # Lambda function
│   ├── lambda_function.py   # Main handler
│   └── requirements.txt     # Dependencies
├── terraform/                # Infrastructure as Code
│   ├── main.tf              # Main resources
│   ├── variables.tf         # Variables
│   └── outputs.tf           # Outputs
├── data/                     # Sample data
│   └── destinations.json    # Destination database
└── README.md                # This file
```

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **Terraform** installed (v1.0+)
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

## Deployment Instructions

### Step 1: Clone and Navigate

```bash
cd /path/to/ai-execution
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Review Deployment Plan

```bash
terraform plan
```

This will show you all resources that will be created:
- S3 bucket for website hosting
- Lambda function for itinerary generation
- API Gateway for REST API
- IAM roles and policies
- CloudWatch log groups

### Step 4: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes approximately 1-2 minutes.

### Step 5: Note the Outputs

After successful deployment, Terraform will output:
- `website_url`: Your website URL
- `api_gateway_url`: Your API endpoint URL

### Step 6: Update Frontend Configuration

1. Copy the `api_gateway_url` from the Terraform output
2. Update `frontend/js/app.js`:

```javascript
const CONFIG = {
    API_ENDPOINT: 'YOUR_API_GATEWAY_URL_HERE'  // Replace this
};
```

3. Re-upload the updated file:

```bash
aws s3 cp ../frontend/js/app.js s3://YOUR_BUCKET_NAME/js/app.js
```

Replace `YOUR_BUCKET_NAME` with the S3 bucket name from Terraform output.

### Step 7: Test Your Application

1. Open the website URL in your browser
2. Fill out the travel preferences form
3. Click "Generate Itinerary"
4. View your personalized travel plan!

## Usage Example

### Input:
- **Destination**: Paris
- **Duration**: 5 days
- **Budget**: Moderate
- **Interests**: Culture, Food
- **Travel Style**: Couple

### Output:
A detailed 5-day itinerary including:
- Day-by-day activities
- Recommended attractions
- Dining suggestions
- Time estimates
- Local tips

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │────────▶│  S3 Website  │         │   Lambda    │
│  (User)     │         │  (Frontend)  │         │  Function   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                         ▲
                               │                         │
                               ▼                         │
                        ┌──────────────┐                 │
                        │ API Gateway  │─────────────────┘
                        └──────────────┘
```

### AWS Resources Created

1. **S3 Bucket**: Hosts static website (HTML, CSS, JS)
2. **Lambda Function**: Processes requests and generates itineraries
3. **API Gateway**: HTTP API for Lambda invocation
4. **IAM Roles**: Permissions for Lambda execution
5. **CloudWatch Logs**: Monitoring and debugging

## Customization

### Adding New Destinations

Edit `backend/lambda_function.py` and add to `DESTINATION_DATA`:

```python
"rome": {
    "name": "Rome",
    "attractions": [
        {"name": "Colosseum", "type": "culture", "time": "2-3 hours"},
        # Add more...
    ],
    "food": ["Pasta carbonara", "Gelato"],
    "tips": "Visit early morning to avoid crowds"
}
```

### Styling Changes

Modify `frontend/css/style.css` and update the S3 object:

```bash
aws s3 cp frontend/css/style.css s3://YOUR_BUCKET_NAME/css/style.css
```

### Budget Adjustment

Update the budget calculations in `lambda_function.py`:

```python
def get_restaurant_by_budget(budget, food_options):
    # Customize restaurant selection logic
```

## Future Enhancements

This basic implementation can be enhanced with:

### 1. LLM Integration
```python
# Add to lambda_function.py
import anthropic  # or import openai

def generate_with_llm(prompt):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    # Fine-tuned model for travel guides
    response = client.messages.create(...)
    return response
```

### 2. RAG System
- Store destination data in vector database (Pinecone, Weaviate)
- Retrieve real-time information
- Semantic search for attractions

### 3. Agent Architecture
- Multi-agent system for itinerary optimization
- Budget calculation agent
- Transportation routing agent
- Accommodation finder agent

### 4. Real-Time Data
- Weather API integration
- Hotel availability check
- Event calendar integration
- Current prices and reviews

## Cost Estimation

Monthly costs (approximate):

- **S3**: $0.023/GB storage + $0.09/GB transfer = ~$1-2/month
- **Lambda**: 1M requests free tier, then $0.20/1M requests
- **API Gateway**: 1M requests free tier, then $1.00/1M requests
- **CloudWatch**: Minimal for basic logging

**Expected monthly cost**: < $5 for moderate traffic

## Monitoring

### View Lambda Logs

```bash
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

### View API Gateway Logs

```bash
aws logs tail /aws/apigateway/travel-itinerary-ai-dev --follow
```

### Check Lambda Metrics

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=FUNCTION_NAME \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Troubleshooting

### Issue: Website not loading

**Solution**: Check S3 bucket policy and public access settings

```bash
aws s3api get-bucket-policy --bucket YOUR_BUCKET_NAME
```

### Issue: API returns CORS error

**Solution**: Verify API Gateway CORS configuration in `main.tf`

### Issue: Lambda timeout

**Solution**: Increase timeout in `main.tf`:

```hcl
resource "aws_lambda_function" "itinerary_generator" {
  timeout = 60  # Increase from 30
}
```

### Issue: Cannot find Terraform resources

**Solution**: Ensure you're in the terraform directory:

```bash
cd terraform
terraform show
```

## Cleanup

To destroy all resources and avoid charges:

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted. All AWS resources will be deleted.

## Development

### Local Testing

Test the Lambda function locally:

```bash
cd backend
python lambda_function.py
```

### Update Lambda Code

After modifying `lambda_function.py`:

```bash
cd terraform
terraform apply -replace="aws_lambda_function.itinerary_generator"
```

## Security Considerations

- S3 bucket is publicly accessible (required for static website)
- API Gateway has CORS enabled for all origins
- No authentication (add API keys or Cognito for production)
- Lambda has minimal IAM permissions
- No sensitive data stored

## Contributing

To extend this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - Feel free to use for personal or commercial projects.

## Support

For issues or questions:
- Check Terraform documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- AWS Lambda docs: https://docs.aws.amazon.com/lambda/
- API Gateway docs: https://docs.aws.amazon.com/apigateway/

## Acknowledgments

- Built with AWS serverless architecture
- Terraform for infrastructure management
- Designed for simplicity and cost-effectiveness

---

**Happy Traveling! 🌍✈️**
