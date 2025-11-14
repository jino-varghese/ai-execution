# ⚖️ Legal Document Review and Contract Analysis Agent

An AI-powered legal document analysis system that assists lawyers and legal professionals by analyzing contracts, identifying potential risks, and providing actionable recommendations. Built with AWS Lambda, AWS Bedrock (Claude AI), and advanced natural language processing.

## ✨ Key Features

### 🤖 LLM Fine-Tuning on Legal Texts
- Powered by **AWS Bedrock (Claude 3 Sonnet)** for deep legal understanding
- Specialized prompting for legal document analysis
- Professional-grade contract interpretation

### 📚 RAG (Retrieval Augmented Generation) for Document Analysis
- Legal precedent matching and retrieval
- Case law reference system
- Contractual template comparisons
- Best practice recommendations

### ⚠️ Risk Assessment Engine
- **Automated Risk Detection**: Identifies potential legal issues
- **Missing Clause Detection**: Flags critical missing protections
- **Risk Scoring**: 0-100 risk assessment with severity levels
- **Smart Pattern Matching**: Detects problematic contract terms

### 💡 Intelligent Analysis
- One-sided indemnification detection
- Unlimited liability clause identification
- Automatic renewal risk assessment
- IP assignment clause analysis
- Non-compete enforceability checks
- Confidentiality scope validation

## 🏗️ Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ↓
┌─────────────────────┐
│ Lambda Function URL │
│  (Public Endpoint)  │
└────────┬────────────┘
         │
         ↓
┌──────────────────────────────┐
│    AWS Lambda (Python)       │
│  ┌────────────────────────┐  │
│  │ Document Processing    │  │
│  │ - Clause Extraction    │  │
│  │ - Risk Identification  │  │
│  │ - Pattern Matching     │  │
│  └────────────────────────┘  │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│    AWS Bedrock (Claude AI)   │
│  - Legal Text Analysis       │
│  - Contract Interpretation   │
│  - Risk Assessment           │
└──────────────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│   RAG System (In-Memory)     │
│  - Legal Precedents DB       │
│  - Best Practices Library    │
│  - Risk Categories           │
└──────────────────────────────┘
```

## 📋 Prerequisites

1. **AWS Account** (Free tier eligible)
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **AWS Bedrock Access** (Request access to Claude 3 Sonnet)
   - Go to AWS Console → Bedrock → Model access
   - Request access to "Anthropic Claude 3 Sonnet"
   - Usually approved instantly
4. **Python 3.11** or later

## 🚀 Quick Start

### Automated Deployment (Recommended)

```bash
# Ensure deploy.sh is executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script automatically:
1. ✅ Verifies AWS credentials
2. ✅ Creates IAM role with Bedrock permissions
3. ✅ Packages dependencies
4. ✅ Deploys Lambda function (512MB, 60s timeout)
5. ✅ Creates public Function URL
6. ✅ Configures CORS for web access

**You'll receive a URL like:** `https://xyz123.lambda-url.us-east-1.on.aws/`

### Manual Deployment (AWS Console)

1. **Create IAM Role**:
   - Go to IAM → Roles → Create Role
   - Select Lambda as trusted entity
   - Attach policies:
     - `AWSLambdaBasicExecutionRole`
     - Custom policy for Bedrock access (see deploy.sh)

2. **Create Lambda Function**:
   - Runtime: Python 3.11
   - Memory: 512 MB
   - Timeout: 60 seconds
   - Upload `lambda_function.py`

3. **Enable Function URL**:
   - Configuration → Function URL → Create
   - Auth type: NONE
   - CORS: Enable

## 🧪 Using the Application

### Web Interface

1. **Open the Function URL** in your browser
2. **Choose an option**:
   - Load a sample contract (NDA, Service Agreement, Employment)
   - Paste your own legal document
3. **Click "Analyze Document"**
4. **Review the AI-powered analysis**:
   - Overall risk score and level
   - AI-generated summary and insights
   - Identified risks with recommendations
   - Missing critical clauses
   - Relevant legal precedents
   - Actionable recommendations

### Sample Contracts Included

- **NDA (Non-Disclosure Agreement)**
- **Service Agreement**
- **Employment Agreement**

## 📊 Analysis Output

### Risk Levels
- **CRITICAL** (70-100): Immediate action required
- **HIGH** (50-69): Significant concerns
- **MEDIUM** (30-49): Review recommended
- **LOW** (0-29): Standard protections present

### Identified Risks
Each risk includes:
- **Type**: Category of legal risk
- **Severity**: HIGH, MEDIUM, or LOW
- **Description**: What the issue is
- **Recommendation**: How to address it

### Critical Clauses Monitored
- Limitation of Liability
- Indemnification
- Termination
- Confidentiality
- Governing Law
- Dispute Resolution
- Intellectual Property
- Payment Terms
- Warranties
- Force Majeure

## 📁 Project Structure

```
legal-document-analyzer/
├── lambda_function.py      # Main AI agent with analysis engine
├── requirements.txt        # Python dependencies (boto3)
├── deploy.sh              # Automated deployment script
├── cleanup.sh             # Resource cleanup script
├── README.md              # This file
├── DEPLOYMENT_GUIDE.md    # Detailed deployment guide
└── PROJECT_OVERVIEW.md    # Technical architecture docs
```

## 🔧 Configuration

### Lambda Configuration
- **Function Name**: `legal-document-analyzer`
- **Runtime**: Python 3.11
- **Memory**: 512 MB (adjustable for larger documents)
- **Timeout**: 60 seconds
- **IAM Role**: Includes Bedrock invoke permissions

### AWS Bedrock Model
- **Model**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Max Tokens**: 2000 (configurable)
- **Temperature**: 0.3 (for consistent legal analysis)

## 💰 Cost Estimate

**Monthly cost for typical usage:** $5-20

| Service | Cost |
|---------|------|
| **Lambda** | $0.20/million requests + $0.0000166667/GB-second |
| **Function URL** | FREE (no API Gateway) |
| **Bedrock (Claude Sonnet)** | $0.003/1K input tokens + $0.015/1K output tokens |
| **CloudWatch Logs** | First 5 GB FREE, then $0.50/GB |

**Example**: 100 contract analyses/month ≈ $2-5

## 📊 Monitoring & Logs

View real-time logs:
```bash
aws logs tail /aws/lambda/legal-document-analyzer --follow --region us-east-1
```

Or in AWS Console:
- CloudWatch → Log Groups → `/aws/lambda/legal-document-analyzer`

## 🛠️ Advanced Features

### 1. Document Processing
```python
# Extracts legal clauses using regex patterns
extract_clauses(document_text)

# Identifies risks using pattern matching and heuristics
identify_risks(document_text)

# Checks for missing critical clauses
check_missing_clauses(document_text)
```

### 2. LLM Integration
```python
# AWS Bedrock Claude analysis
get_llm_analysis(text, doc_type)
```

### 3. RAG System
```python
# Legal precedent retrieval
get_relevant_precedents(clauses, risks)
```

### 4. Risk Scoring
```python
# Calculates 0-100 risk score
calculate_risk_score(risks, missing_clauses)
```

## 🧹 Cleanup

Remove all AWS resources:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

This deletes:
- Lambda function
- IAM role and policies
- Function URL configuration

## 🔒 Security Best Practices

### Current Setup (Demo/Testing)
- ✅ Public Function URL for easy access
- ✅ IAM role with least privilege
- ✅ No hardcoded credentials
- ✅ Environment-based configuration

### For Production
- 🔐 Add authentication (Cognito, API Key)
- 🔐 Implement rate limiting
- 🔐 Use AWS WAF for protection
- 🔐 Enable CloudWatch alarms
- 🔐 Encrypt sensitive documents (S3 + KMS)
- 🔐 Add audit logging (CloudTrail)
- 🔐 Implement document retention policies
- 🔐 Use VPC for enhanced security

## 📚 Learning Resources

### AWS Documentation
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

### Legal AI Concepts
- RAG (Retrieval Augmented Generation)
- LLM Fine-tuning techniques
- Natural Language Processing for legal texts
- Contract analysis best practices

## 🚀 Enhancement Ideas

### 1. Document Upload Support
```python
# Add PDF/DOCX parsing
import PyPDF2, python-docx
```

### 2. Vector Database Integration
```python
# Use Pinecone or ChromaDB for better RAG
import chromadb
```

### 3. Multi-Document Comparison
```python
# Compare multiple contracts
compare_contracts(contract1, contract2)
```

### 4. Export Analysis Reports
```python
# Generate PDF reports
generate_pdf_report(analysis_results)
```

### 5. Real Legal Database
```python
# Connect to LexisNexis, Westlaw APIs
# Retrieve real case law and precedents
```

## 🐛 Troubleshooting

### Bedrock Access Denied
```bash
# Verify model access is enabled
aws bedrock list-foundation-models --region us-east-1

# Check IAM role has bedrock:InvokeModel permission
aws iam get-role-policy --role-name legal-document-analyzer-role --policy-name BedrockAccess
```

### Function Timeout
```bash
# Increase timeout for large documents
aws lambda update-function-configuration \
    --function-name legal-document-analyzer \
    --timeout 120 \
    --region us-east-1
```

### Memory Issues
```bash
# Increase memory for complex analysis
aws lambda update-function-configuration \
    --function-name legal-document-analyzer \
    --memory-size 1024 \
    --region us-east-1
```

### CORS Errors
```bash
# Update CORS configuration
aws lambda update-function-url-config \
    --function-name legal-document-analyzer \
    --cors AllowOrigins="*",AllowMethods="GET,POST",AllowHeaders="content-type" \
    --region us-east-1
```

## 🎯 What You'll Learn

By deploying this project, you'll gain hands-on experience with:

1. **AWS Lambda**: Serverless architecture, function URLs
2. **AWS Bedrock**: Foundation models, Claude AI integration
3. **Legal AI**: Contract analysis, risk assessment
4. **RAG Systems**: Retrieval augmented generation
5. **NLP Techniques**: Pattern matching, clause extraction
6. **IAM Security**: Role-based access control
7. **Serverless Deployment**: Infrastructure automation
8. **AI Prompting**: Legal domain prompting strategies

## 📈 Use Cases

### For Legal Professionals
- Quick contract review and risk assessment
- Identify missing standard clauses
- Compare against legal best practices
- Generate initial analysis reports

### For Businesses
- Vendor contract review
- Employment agreement verification
- NDA risk assessment
- Service agreement analysis

### For Developers
- Learn AI integration patterns
- Practice AWS serverless architecture
- Understand RAG implementation
- Explore legal tech applications

## ⚠️ Disclaimer

This tool is designed to **assist** legal professionals, not replace them. Always:
- Have qualified attorneys review contracts
- Verify AI-generated insights
- Consider jurisdiction-specific requirements
- Consult legal experts for final decisions

This is an educational/assistive tool, not legal advice.

## 📧 Support

- Check `DEPLOYMENT_GUIDE.md` for detailed setup
- Review AWS Lambda documentation
- Check CloudWatch logs for errors
- Verify Bedrock model access

## 🤝 Contributing

Enhancement ideas welcome:
- Add more risk detection patterns
- Expand legal precedent database
- Improve clause extraction accuracy
- Add support for more document types
- Integrate with legal databases

## 📝 License

MIT License - Free for learning, research, and commercial use.

## 🎓 Next Steps

After mastering this agent:

1. **Add Document Storage**: Use S3 for document archival
2. **Build Analysis History**: Track analyses in DynamoDB
3. **Create User Accounts**: Add Cognito authentication
4. **Generate PDF Reports**: Export analysis to PDF
5. **Add Email Notifications**: Use SES for alerts
6. **Multi-Language Support**: Analyze contracts in different languages
7. **Advanced RAG**: Integrate with vector databases
8. **Fine-Tune Models**: Custom legal domain fine-tuning

---

**Built with AWS + AI for the Legal Industry** ⚖️

*Empowering legal professionals with AI-powered document analysis*
