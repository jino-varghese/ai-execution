# Quick Start Guide

Get your AI Travel Itinerary Generator up and running in 5 minutes!

## Prerequisites

1. AWS Account
2. AWS CLI configured (`aws configure`)
3. Terraform installed

## Deployment (3 Steps)

### Option 1: Automated Script

```bash
./deploy.sh
```

Follow the prompts!

### Option 2: Manual Deployment

```bash
# 1. Initialize Terraform
cd terraform
terraform init

# 2. Deploy
terraform apply

# 3. Note the outputs (save these!)
```

## Post-Deployment

### Update Frontend Configuration

1. Copy the `api_gateway_url` from Terraform output

2. Edit `frontend/js/app.js` line 2:
   ```javascript
   API_ENDPOINT: 'YOUR_API_URL_HERE'
   ```

3. Upload to S3:
   ```bash
   aws s3 cp frontend/js/app.js s3://BUCKET_NAME/js/app.js
   ```

## Test Your App

1. Open the website URL (from Terraform output)
2. Fill in travel details:
   - Destination: Paris
   - Duration: 5 days
   - Budget: Moderate
   - Interests: Culture, Food
3. Click "Generate Itinerary"
4. View your personalized plan!

## Cleanup

```bash
./destroy.sh
```

Or manually:

```bash
cd terraform
terraform destroy
```

## Troubleshooting

**Problem**: API not working
- **Solution**: Make sure you updated `app.js` with the correct API URL

**Problem**: Website not loading
- **Solution**: Check S3 bucket is publicly accessible

**Problem**: Terraform errors
- **Solution**: Ensure AWS credentials are configured correctly

## Cost

Expected cost: **< $5/month** for moderate usage

Free tier covers most usage for new AWS accounts.

## Next Steps

- Add more destinations in `backend/lambda_function.py`
- Customize styling in `frontend/css/style.css`
- Integrate real LLM (OpenAI, Anthropic)
- Add user authentication
- Implement RAG with vector database

## Need Help?

See the full [README.md](README.md) for detailed documentation.

---

**Happy Deploying! 🚀**
