# AI Implementation Guide - Amazon Bedrock LLM Integration

This document explains the AI-powered features of the Travel Itinerary Generator, specifically the integration with Amazon Bedrock and the RAG (Retrieval-Augmented Generation) system.

## Overview

The application implements a sophisticated AI architecture combining:

1. **LLM (Large Language Model)**: Amazon Bedrock with Claude 3 Sonnet
2. **RAG (Retrieval-Augmented Generation)**: Custom knowledge base for destination data
3. **Agent Behavior**: Personalization engine based on user preferences
4. **Fallback System**: Template-based generation if Bedrock is unavailable

## Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│  Lambda Function Entry Point            │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  1. RAG Retrieval                       │
│     - Query knowledge base              │
│     - Filter by destination             │
│     - Match attractions to interests    │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  2. Prompt Engineering                  │
│     - Build context from RAG data       │
│     - Include user preferences          │
│     - Format instructions for LLM       │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  3. Amazon Bedrock LLM                  │
│     - Claude 3 Sonnet model             │
│     - Generate personalized itinerary   │
│     - JSON-formatted output             │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│  4. Response Processing                 │
│     - Parse JSON response               │
│     - Add metadata                      │
│     - Return to user                    │
└─────────────────────────────────────────┘
```

## Key Components

### 1. RAG (Retrieval-Augmented Generation)

**What is RAG?**
RAG combines information retrieval with LLM generation. Instead of relying solely on the model's training data, we retrieve relevant information from a knowledge base and include it in the prompt.

**Implementation:**

```python
def retrieve_destination_knowledge(destination):
    """
    Retrieves destination-specific information from knowledge base
    - Exact matching on destination name
    - Partial matching for variations
    - Returns structured data with attractions, tips, costs
    """
```

**Knowledge Base Structure:**
```python
DESTINATION_KNOWLEDGE_BASE = {
    "paris": {
        "name": "Paris",
        "country": "France",
        "description": "...",
        "attractions": [
            {
                "name": "Eiffel Tower",
                "category": "landmark",
                "description": "...",
                "time_needed": "2-3 hours",
                "best_time": "Early morning or sunset",
                "avg_cost": "€26-34"
            }
        ],
        "dining": {...},
        "transportation": {...},
        "tips": [...],
        "budget_estimate": {...}
    }
}
```

**Benefits:**
- **Accuracy**: Grounded in verified destination data
- **Freshness**: Easy to update knowledge base
- **Cost**: Reduces tokens sent to LLM
- **Relevance**: Filters data based on user interests

### 2. Interest-Based Filtering

**Smart Attraction Matching:**

```python
def filter_attractions_by_interests(attractions, interests):
    """
    Scores attractions based on relevance to user interests
    - Category matching: +2 points
    - Description matching: +1 point
    - Returns top-scored attractions
    """
```

**Example:**
```
User Interests: ["culture", "food"]

Attractions Scoring:
- Louvre Museum (culture) → Score: 2
- Latin Quarter (food) → Score: 2
- Eiffel Tower (landmark) → Score: 0
- Seine River Cruise (relaxation) → Score: 0

Result: Prioritizes museums and food experiences
```

### 3. LLM Prompt Engineering

**Prompt Structure:**

```
[User Preferences]
- Destination, Duration, Budget, Interests, Style

[RAG Context - Retrieved Knowledge]
- Destination details
- Filtered attractions (top 10 by interest match)
- Dining options for budget level
- Transportation info
- Local tips
- Budget estimates

[Instructions]
- Create detailed day-by-day itinerary
- Match budget level
- Focus on user interests
- Include practical tips
- Output as JSON
```

**Prompt Engineering Techniques Used:**

1. **Few-shot Learning**: Provide expected output format
2. **Structured Output**: Request JSON for easy parsing
3. **Contextual Grounding**: Include RAG data for accuracy
4. **Constraint Setting**: Budget, interests, travel style
5. **Task Decomposition**: Break into days and activities

### 4. Amazon Bedrock Integration

**Model Configuration:**

```python
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4000,           # Long itineraries need more tokens
    "temperature": 0.7,            # Balance creativity and consistency
    "messages": [...]
}
```

**Why Claude 3 Sonnet?**
- **Balanced Performance**: Good quality/cost ratio
- **Long Context**: Can handle extensive RAG data
- **JSON Output**: Excellent at structured responses
- **Travel Knowledge**: Strong general knowledge base
- **Cost-Effective**: ~$3 per 1M input tokens

**Alternative Models:**
- **Claude 3 Haiku**: Faster, cheaper, for simple itineraries
- **Claude 3 Opus**: Highest quality, for premium features

### 5. Fallback System

**Why Fallback?**
- Bedrock service unavailable
- API quota exceeded
- Regional availability issues
- Cost optimization (use template for simple requests)

**Implementation:**

```python
try:
    # Call Bedrock
    itinerary = call_bedrock_llm(prompt)
except Exception as e:
    # Fallback to template-based generation
    itinerary = generate_fallback_itinerary(...)
```

**Fallback Features:**
- Uses same RAG knowledge base
- Template-based day planning
- Still personalized by interests
- Marks as "ai_generated": false

## Implementation Details

### Lambda Function Configuration

**Resource Requirements:**
- **Memory**: 512 MB (Bedrock API calls need more memory)
- **Timeout**: 60 seconds (LLM inference can take 10-30 seconds)
- **Runtime**: Python 3.11
- **Dependencies**: boto3 (pre-installed in Lambda)

**IAM Permissions Required:**

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
  ]
}
```

### Cost Analysis

**Per Request Costs:**

1. **Lambda Execution**
   - 512 MB × 10 seconds = ~$0.00001667

2. **Bedrock API (Claude 3 Sonnet)**
   - Input: ~3,000 tokens × $0.003/1K = $0.009
   - Output: ~1,000 tokens × $0.015/1K = $0.015
   - **Total per request: ~$0.024**

3. **API Gateway**
   - $0.000001 per request

**Monthly Cost Estimates:**
- 100 requests/month: ~$2.50
- 1,000 requests/month: ~$25
- 10,000 requests/month: ~$250

**Cost Optimization Tips:**
1. Use fallback for repeat requests (cache results)
2. Switch to Claude 3 Haiku for simple queries (3x cheaper)
3. Reduce max_tokens for shorter trips
4. Implement request caching

### Regional Availability

**Bedrock Regions:**
Amazon Bedrock is available in:
- `us-east-1` (N. Virginia) ✅
- `us-west-2` (Oregon) ✅
- `eu-central-1` (Frankfurt) ✅
- `ap-southeast-1` (Singapore) ✅
- `ap-northeast-1` (Tokyo) ✅

**Deployment Note:**
Default region is `us-east-1`. To change:

```hcl
# terraform/variables.tf
variable "aws_region" {
  default = "us-west-2"  # Change this
}
```

## Feature Highlights

### ✅ LLM Fine-Tuning (via Prompt Engineering)

While we don't use traditional fine-tuning, our implementation achieves similar results through:

1. **In-Context Learning**: Rich context in every prompt
2. **Domain-Specific Knowledge**: RAG provides travel expertise
3. **Structured Templates**: Consistent output format
4. **Few-Shot Examples**: JSON format specification

**Future Enhancement:**
- Fine-tune custom model on travel guides corpus
- Use Amazon Bedrock Custom Models
- Train on historical itineraries for style matching

### ✅ RAG for Real-Time Information

Current implementation:
- Static knowledge base with verified data
- Filtered by user interests
- Updated manually

**Future Enhancement:**
- Integrate external APIs (weather, events, prices)
- Use vector database (Pinecone, Weaviate)
- Semantic search for attractions
- Real-time price checking
- Event calendar integration

### ✅ Agent for Custom Itinerary Creation

Current implementation:
- Single-agent architecture
- Personalization via prompt engineering
- Interest-based filtering

**Future Enhancement:**
- **Multi-Agent System:**
  - Budget Agent: Optimizes costs
  - Route Agent: Minimizes travel time
  - Activity Agent: Matches preferences
  - Dining Agent: Recommends restaurants
  - Coordinator Agent: Assembles final plan

## Testing

### Local Testing

```bash
cd backend
python lambda_function.py
```

This will:
1. Use fallback system (no AWS credentials needed)
2. Test RAG retrieval
3. Generate sample itinerary
4. Output JSON to console

### AWS Testing

```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name travel-itinerary-ai-itinerary-generator-dev \
  --payload '{"destination":"Paris","duration":5,"budget":"moderate","interests":["culture","food"],"travelStyle":"couple"}' \
  response.json

# View response
cat response.json | jq
```

### Example Request/Response

**Request:**
```json
{
  "destination": "Paris",
  "duration": 5,
  "budget": "moderate",
  "interests": ["culture", "food"],
  "travelStyle": "couple",
  "preferences": "romantic experiences, avoid crowds"
}
```

**Response:**
```json
{
  "destination": "Paris",
  "duration": 5,
  "budget": "moderate",
  "summary": "A romantic 5-day escape to Paris...",
  "days": [
    {
      "day": 1,
      "title": "Arrival & Montmartre",
      "activities": [
        {
          "time": "Morning",
          "activity": "Arrive in Paris",
          "description": "Check into boutique hotel..."
        }
      ]
    }
  ],
  "tips": "Book Louvre tickets online...",
  "estimated_total_cost": "€1,000-1,750 per person",
  "ai_generated": true,
  "model": "Amazon Bedrock - Claude 3 Sonnet",
  "knowledge_source": "RAG"
}
```

## Troubleshooting

### Issue: "Bedrock model not available"

**Solution:**
1. Check if Bedrock is enabled in your AWS region
2. Go to AWS Console → Bedrock → Model Access
3. Request access to Claude 3 Sonnet
4. Wait for approval (usually instant)

### Issue: "Lambda timeout"

**Solution:**
1. Increase timeout in terraform/main.tf:
   ```hcl
   timeout = 90  # seconds
   ```
2. Check CloudWatch logs for bottlenecks
3. Consider caching frequent requests

### Issue: "IAM permissions error"

**Solution:**
1. Verify Bedrock policy is attached to Lambda role
2. Check AWS region matches in ARN
3. Ensure model ID is correct

### Issue: "Fallback always used"

**Solution:**
1. Check Lambda CloudWatch logs for errors
2. Verify Bedrock credentials
3. Test Bedrock access:
   ```bash
   aws bedrock-runtime invoke-model \
     --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
     --body '{"prompt":"Hello"}' \
     --region us-east-1 \
     output.json
   ```

## Monitoring

### CloudWatch Metrics

**Lambda Metrics:**
- Invocations
- Duration (should be 10-30s with Bedrock)
- Errors
- Throttles

**Custom Logs:**
```python
print(f"Generating itinerary for {destination}")  # Entry
print(f"RAG retrieved {len(knowledge)} items")   # RAG stats
print(f"Bedrock API error: {str(e)}")            # Errors
```

**View Logs:**
```bash
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

### Cost Monitoring

**Set up billing alerts:**
1. AWS Console → Billing → Budgets
2. Create budget: $50/month
3. Alert at 80% threshold

**Track Bedrock costs:**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://bedrock-filter.json
```

## Future Enhancements

### Phase 1: Enhanced RAG
- [ ] Vector database integration (Pinecone)
- [ ] Semantic search for attractions
- [ ] Real-time data APIs (weather, events)
- [ ] User review integration (TripAdvisor API)

### Phase 2: Multi-Agent System
- [ ] Budget optimization agent
- [ ] Route planning agent
- [ ] Restaurant recommendation agent
- [ ] Activity personalization agent
- [ ] Agent coordination layer

### Phase 3: Fine-Tuning
- [ ] Collect historical itineraries
- [ ] Fine-tune on travel guides corpus
- [ ] Use Bedrock Custom Models
- [ ] A/B test vs prompt engineering

### Phase 4: Advanced Features
- [ ] Multi-destination trips
- [ ] Real-time booking integration
- [ ] Collaborative itineraries
- [ ] Mobile app support
- [ ] Offline mode

## References

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3 Model Card](https://www.anthropic.com/claude)
- [RAG Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/rag.html)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**Built with Amazon Bedrock • Powered by Claude 3 Sonnet • Enhanced with RAG**
