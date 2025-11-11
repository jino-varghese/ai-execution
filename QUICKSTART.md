# ⚡ Quick Start Cheat Sheet

## 🎯 One-Command Deployment

```bash
./deploy.sh
```

That's it! You'll get a live URL in ~2 minutes.

---

## 📝 Prerequisites Checklist

- [ ] AWS Account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] OpenWeatherMap API key (https://openweathermap.org/api)
- [ ] Python 3.11+ installed

---

## 🚀 Deployment Options

### Option A: Automated (Recommended)
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Follow the prompts
# Enter OpenWeatherMap API key when asked
```

### Option B: AWS CLI Manual
```bash
# Package dependencies
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r ../function.zip . && cd ..

# Create function
aws lambda create-function \
  --function-name gen-ai-dashboard \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# Create Function URL
aws lambda create-function-url-config \
  --function-name gen-ai-dashboard \
  --auth-type NONE

# Add public permission
aws lambda add-permission \
  --function-name gen-ai-dashboard \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE
```

### Option C: AWS Console
1. AWS Console → Lambda → Create function
2. Upload `function.zip`
3. Configuration → Function URL → Create
4. Set auth type to NONE
5. Add environment variable: `OPENWEATHER_API_KEY`

---

## 🧪 Testing

```bash
# Get your Function URL
aws lambda get-function-url-config \
  --function-name gen-ai-dashboard \
  --query FunctionUrl

# Or just open the URL from deploy.sh output
```

**Expected Result:**
- ✅ Page loads with gradient background
- ✅ Current time displays and updates
- ✅ Houston weather shows temperature
- ✅ 6 Gen AI service cards visible
- ✅ Clicking card highlights it
- ✅ "Launch Selected Service" button works

---

## 📊 Monitoring

### View Logs (Real-time)
```bash
aws logs tail /aws/lambda/gen-ai-dashboard --follow
```

### View Recent Logs
```bash
aws logs tail /aws/lambda/gen-ai-dashboard --since 1h
```

### Check Function Status
```bash
aws lambda get-function --function-name gen-ai-dashboard
```

---

## 🔧 Common Updates

### Update Code
```bash
# Make changes to lambda_function.py
# Re-run deployment
./deploy.sh
```

### Update Environment Variable
```bash
aws lambda update-function-configuration \
  --function-name gen-ai-dashboard \
  --environment Variables={OPENWEATHER_API_KEY=your_new_key}
```

### Update Timeout
```bash
aws lambda update-function-configuration \
  --function-name gen-ai-dashboard \
  --timeout 60
```

---

## 🧹 Cleanup

```bash
# Delete everything
./cleanup.sh

# Or manually
aws lambda delete-function --function-name gen-ai-dashboard
aws iam delete-role --role-name lambda-gen-ai-dashboard-role
```

---

## 🐛 Troubleshooting

### Issue: Weather shows "N/A"
```bash
# Check if API key is set
aws lambda get-function-configuration \
  --function-name gen-ai-dashboard \
  --query Environment.Variables.OPENWEATHER_API_KEY
```

### Issue: Function timeout
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name gen-ai-dashboard \
  --timeout 30
```

### Issue: Permission denied
```bash
# Make scripts executable
chmod +x deploy.sh cleanup.sh
```

### Issue: AWS credentials not found
```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity
```

---

## 📚 File Structure

```
├── lambda_function.py      ← Main app (HTML + Python)
├── requirements.txt        ← Dependencies (urllib3)
├── deploy.sh              ← Automated deployment
├── cleanup.sh             ← Resource cleanup
├── README.md              ← Full documentation
├── DEPLOYMENT_GUIDE.md    ← Detailed steps
└── architecture.html      ← Visual architecture
```

---

## 💡 Quick Customizations

### Change Location (Edit lambda_function.py)
```python
# Line ~35
lat = 29.7604  # Your latitude
lon = -95.3698  # Your longitude
```

### Add Your Name
```python
# Line ~110 in HTML
<h1>🚀 [Your Name]'s AWS Dashboard</h1>
```

### Change Colors
```python
# Line ~130 in CSS
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

---

## 🎓 Learning Path

1. **Week 1**: Deploy this dashboard ✅
2. **Week 2**: Add Bedrock API call for AI text
3. **Week 3**: Integrate DynamoDB for data storage
4. **Week 4**: Add S3 for file uploads
5. **Week 5**: Build a full chatbot with Lex

---

## 📞 Getting Help

- **AWS Issues**: Check CloudWatch logs
- **Deployment Issues**: See DEPLOYMENT_GUIDE.md
- **Code Issues**: Review lambda_function.py comments
- **AWS Support**: AWS Support Center

---

## 🎯 Success Metrics

After deployment, you should be able to:
- ✅ Access a live web application
- ✅ See real-time Houston weather
- ✅ Click and select Gen AI services
- ✅ Understand Lambda function structure
- ✅ Monitor logs in CloudWatch
- ✅ Update and redeploy changes

---

## 💰 Cost Reminder

**Monthly cost for this project: < $1**

- Lambda: First 1M requests FREE
- Function URL: FREE
- Weather API: FREE tier
- CloudWatch: FREE tier (5GB logs)

---

## 🚀 Next Projects

Build these to level up:

1. **AI Chatbot**: Use Bedrock for conversations
2. **Image Analyzer**: Upload images, use Rekognition
3. **Sentiment Dashboard**: Analyze text with Comprehend
4. **Voice Assistant**: Combine Lex + Polly
5. **Full Stack App**: Add React frontend + API Gateway

---

**Good luck with your AWS Gen AI learning journey! 🎉**

Need help? Check the full README.md for detailed explanations.
