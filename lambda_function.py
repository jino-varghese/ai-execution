import json
import boto3
import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re
import traceback

# Initialize AWS clients (lazy initialization to avoid errors at import)
bedrock_runtime = None
s3_client = None

def get_bedrock_client():
    """Lazy initialization of Bedrock client"""
    global bedrock_runtime
    if bedrock_runtime is None:
        try:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {str(e)}")
            bedrock_runtime = None
    return bedrock_runtime

# Legal risk categories and patterns
RISK_CATEGORIES = {
    'indemnification': [
        r'indemnif(?:y|ication)',
        r'hold\s+harmless',
        r'defend\s+against',
    ],
    'limitation_of_liability': [
        r'limitation\s+of\s+liability',
        r'consequential\s+damages',
        r'indirect\s+damages',
        r'liability\s+cap',
    ],
    'termination': [
        r'termination',
        r'cancellation',
        r'notice\s+period',
        r'cure\s+period',
    ],
    'confidentiality': [
        r'confidential(?:ity)?',
        r'proprietary\s+information',
        r'non-disclosure',
        r'NDA',
    ],
    'intellectual_property': [
        r'intellectual\s+property',
        r'IP\s+rights',
        r'copyright',
        r'patent',
        r'trademark',
    ],
    'payment_terms': [
        r'payment\s+terms',
        r'invoice',
        r'late\s+fee',
        r'interest\s+rate',
    ],
    'governing_law': [
        r'governing\s+law',
        r'jurisdiction',
        r'venue',
        r'dispute\s+resolution',
    ],
    'warranties': [
        r'warrant(?:y|ies)',
        r'representation',
        r'guarantee',
    ],
    'force_majeure': [
        r'force\s+majeure',
        r'act\s+of\s+god',
        r'extraordinary\s+event',
    ],
}

# Critical missing clauses
CRITICAL_CLAUSES = [
    'limitation of liability',
    'indemnification',
    'termination',
    'confidentiality',
    'governing law',
    'dispute resolution',
]

# Legal precedents database (simplified for demo)
LEGAL_PRECEDENTS = {
    'indemnification': {
        'description': 'Indemnification clauses protect parties from liability',
        'best_practice': 'Should be mutual and limited in scope',
        'risk_level': 'HIGH',
        'precedent': 'One-sided indemnification clauses may be unenforceable in certain jurisdictions'
    },
    'limitation_of_liability': {
        'description': 'Limits the financial exposure of parties',
        'best_practice': 'Should include carve-outs for gross negligence and willful misconduct',
        'risk_level': 'HIGH',
        'precedent': 'Courts may invalidate liability caps that are unreasonably low'
    },
    'termination': {
        'description': 'Defines how and when the contract can be ended',
        'best_practice': 'Should include notice periods and cure provisions',
        'risk_level': 'MEDIUM',
        'precedent': 'Termination for convenience should be available to both parties'
    },
}


def lambda_handler(event, context):
    """
    Main Lambda handler for Legal Document Analysis

    Endpoints:
    - GET / : Returns the web UI
    - POST /analyze : Analyzes uploaded legal document
    - POST /risk-assessment : Performs detailed risk assessment
    """

    # Standard CORS headers for all responses
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    try:
        # Log the incoming event for debugging
        # Support both API Gateway (httpMethod) and Lambda Function URL (requestContext.http.method) formats
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('path') or event.get('rawPath', '/')
        print(f"Request: {http_method} {path}")

        # Handle OPTIONS for CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'OK'})
            }

        if http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': get_html_ui()
            }

        elif http_method == 'POST':
            # Parse request body with better error handling
            try:
                body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'Invalid JSON in request body',
                        'details': str(e)
                    })
                }

            # Log the request for debugging
            print(f"POST request received. Body keys: {list(body.keys())}")

            if 'document' in body:
                # Analyze document
                try:
                    result = analyze_document(body)
                    return {
                        'statusCode': 200,
                        'headers': cors_headers,
                        'body': json.dumps(result)
                    }
                except Exception as e:
                    print(f"Error in analyze_document: {str(e)}")
                    print(traceback.format_exc())
                    return {
                        'statusCode': 500,
                        'headers': cors_headers,
                        'body': json.dumps({
                            'error': 'Analysis failed',
                            'details': str(e),
                            'type': type(e).__name__
                        })
                    }

            elif 'text' in body:
                # Quick risk assessment
                try:
                    result = quick_risk_assessment(body['text'])
                    return {
                        'statusCode': 200,
                        'headers': cors_headers,
                        'body': json.dumps(result)
                    }
                except Exception as e:
                    print(f"Error in quick_risk_assessment: {str(e)}")
                    return {
                        'statusCode': 500,
                        'headers': cors_headers,
                        'body': json.dumps({
                            'error': 'Risk assessment failed',
                            'details': str(e)
                        })
                    }
            else:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'error': 'No document or text provided',
                        'received_keys': list(body.keys())
                    })
                }

        else:
            return {
                'statusCode': 405,
                'headers': cors_headers,
                'body': json.dumps({'error': f'Method {http_method} not allowed'})
            }

    except Exception as e:
        print(f"Unhandled exception in lambda_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'type': type(e).__name__
            })
        }


def analyze_document(data: Dict) -> Dict[str, Any]:
    """
    Comprehensive document analysis using LLM and RAG
    """
    document_text = data.get('document', '')
    document_type = data.get('type', 'contract')

    # Extract key clauses
    clauses = extract_clauses(document_text)

    # Identify risks
    risks = identify_risks(document_text)

    # Check for missing critical clauses
    missing_clauses = check_missing_clauses(document_text)

    # Get LLM analysis
    llm_analysis = get_llm_analysis(document_text, document_type)

    # RAG-based precedent matching
    relevant_precedents = get_relevant_precedents(clauses, risks)

    # Overall risk score
    risk_score = calculate_risk_score(risks, missing_clauses)

    return {
        'analysis_id': f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'timestamp': datetime.now().isoformat(),
        'document_type': document_type,
        'risk_score': risk_score,
        'risk_level': get_risk_level(risk_score),
        'identified_clauses': clauses,
        'identified_risks': risks,
        'missing_critical_clauses': missing_clauses,
        'llm_analysis': llm_analysis,
        'relevant_precedents': relevant_precedents,
        'recommendations': generate_recommendations(risks, missing_clauses),
    }


def quick_risk_assessment(text: str) -> Dict[str, Any]:
    """
    Quick risk assessment for shorter text snippets
    """
    risks = identify_risks(text)
    missing = check_missing_clauses(text)
    risk_score = calculate_risk_score(risks, missing)

    return {
        'risk_score': risk_score,
        'risk_level': get_risk_level(risk_score),
        'identified_risks': risks,
        'missing_clauses': missing,
    }


def extract_clauses(text: str) -> List[Dict[str, str]]:
    """
    Extract legal clauses from document using pattern matching
    """
    clauses = []

    for category, patterns in RISK_CATEGORIES.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around match (150 chars before and after)
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()

                clauses.append({
                    'category': category,
                    'matched_text': match.group(),
                    'context': context,
                    'position': match.start()
                })
                break  # Only take first match per category

    return clauses


def identify_risks(text: str) -> List[Dict[str, Any]]:
    """
    Identify potential legal risks in the document
    """
    risks = []

    # Check for one-sided indemnification
    if re.search(r'shall\s+indemnify', text, re.IGNORECASE):
        if not re.search(r'mutual(?:ly)?\s+indemnif', text, re.IGNORECASE):
            risks.append({
                'type': 'one_sided_indemnification',
                'severity': 'HIGH',
                'description': 'Document contains one-sided indemnification clause',
                'recommendation': 'Negotiate for mutual indemnification'
            })

    # Check for unlimited liability
    if not re.search(r'limitation\s+of\s+liability', text, re.IGNORECASE):
        risks.append({
            'type': 'unlimited_liability',
            'severity': 'HIGH',
            'description': 'No limitation of liability clause found',
            'recommendation': 'Add liability cap to limit exposure'
        })

    # Check for automatic renewal
    if re.search(r'automatic(?:ally)?\s+renew', text, re.IGNORECASE):
        if not re.search(r'opt[- ]out|notice\s+of\s+non[- ]renewal', text, re.IGNORECASE):
            risks.append({
                'type': 'automatic_renewal',
                'severity': 'MEDIUM',
                'description': 'Automatic renewal without clear opt-out provisions',
                'recommendation': 'Ensure clear notice requirements for non-renewal'
            })

    # Check for broad confidentiality
    if re.search(r'all\s+information.*confidential', text, re.IGNORECASE):
        risks.append({
            'type': 'overly_broad_confidentiality',
            'severity': 'MEDIUM',
            'description': 'Overly broad confidentiality obligations',
            'recommendation': 'Define specific categories of confidential information'
        })

    # Check for IP assignment
    if re.search(r'assign|transfer.*intellectual\s+property|IP', text, re.IGNORECASE):
        risks.append({
            'type': 'ip_assignment',
            'severity': 'HIGH',
            'description': 'Intellectual property assignment clause detected',
            'recommendation': 'Review IP ownership and assignment terms carefully'
        })

    # Check for non-compete clauses
    if re.search(r'non[- ]compete|covenant\s+not\s+to\s+compete', text, re.IGNORECASE):
        risks.append({
            'type': 'non_compete',
            'severity': 'MEDIUM',
            'description': 'Non-compete clause found',
            'recommendation': 'Verify enforceability in relevant jurisdiction'
        })

    return risks


def check_missing_clauses(text: str) -> List[str]:
    """
    Check for missing critical clauses
    """
    missing = []

    for clause in CRITICAL_CLAUSES:
        pattern = clause.replace(' ', r'\s+')
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(clause)

    return missing


def get_llm_analysis(text: str, doc_type: str) -> Dict[str, str]:
    """
    Use AWS Bedrock (Claude) for detailed legal analysis
    """
    try:
        # Get Bedrock client
        client = get_bedrock_client()

        if client is None:
            print("Bedrock client not available, using fallback analysis")
            return generate_fallback_analysis(text, doc_type)

        # Truncate text if too long (Claude has token limits)
        max_chars = 8000
        truncated_text = text[:max_chars] if len(text) > max_chars else text

        prompt = f"""You are an expert legal analyst reviewing a {doc_type}.

Please analyze the following document and provide:

1. **Summary**: Brief overview of the document's purpose
2. **Key Terms**: Main obligations and rights of each party
3. **Potential Issues**: Any problematic clauses or missing protections
4. **Overall Assessment**: Your professional opinion on the fairness and completeness

Document:
{truncated_text}

Provide a structured analysis in clear, professional language."""

        # Call AWS Bedrock (Claude)
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
        }

        print(f"Calling Bedrock with model: anthropic.claude-3-sonnet-20240229-v1:0")

        response = client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        analysis = response_body['content'][0]['text']

        print(f"Bedrock analysis successful, length: {len(analysis)}")

        return {
            'summary': analysis,
            'model': 'claude-3-sonnet',
            'confidence': 'high'
        }

    except Exception as e:
        # Fallback analysis if Bedrock is not available
        print(f"Bedrock error: {str(e)}, using fallback analysis")
        print(traceback.format_exc())
        return generate_fallback_analysis(text, doc_type)


def generate_fallback_analysis(text: str, doc_type: str) -> Dict[str, str]:
    """
    Generate a basic analysis when Bedrock is not available
    """
    word_count = len(text.split())
    has_indemnification = bool(re.search(r'indemnif', text, re.IGNORECASE))
    has_liability_limit = bool(re.search(r'limitation\s+of\s+liability', text, re.IGNORECASE))
    has_termination = bool(re.search(r'termination', text, re.IGNORECASE))
    has_governing_law = bool(re.search(r'governing\s+law', text, re.IGNORECASE))

    analysis = f"""**Pattern-Based Analysis** (AI analysis unavailable)

**Summary**: This {doc_type} contains approximately {word_count} words.

**Key Terms Detected**:
- Indemnification clause: {'Yes' if has_indemnification else 'No'}
- Limitation of liability: {'Yes' if has_liability_limit else 'No'}
- Termination provisions: {'Yes' if has_termination else 'No'}
- Governing law: {'Yes' if has_governing_law else 'No'}

**Potential Issues**: Please review the detailed risk assessment below for specific concerns.

**Overall Assessment**: Pattern-based analysis completed. For detailed AI analysis, please ensure AWS Bedrock access is enabled with Claude 3 Sonnet model.

**Note**: This is a fallback analysis. To enable full AI-powered analysis:
1. Go to AWS Console → Bedrock
2. Click 'Model access' → 'Manage model access'
3. Enable 'Anthropic Claude 3 Sonnet'
4. Redeploy or update the Lambda function
"""

    return {
        'summary': analysis,
        'model': 'pattern-based-fallback',
        'confidence': 'medium'
    }


def get_relevant_precedents(clauses: List[Dict], risks: List[Dict]) -> List[Dict]:
    """
    RAG-based retrieval of relevant legal precedents
    """
    precedents = []

    # Simple precedent matching based on identified clauses and risks
    clause_categories = {c['category'] for c in clauses}
    risk_types = {r['type'] for r in risks}

    for category in clause_categories:
        if category in LEGAL_PRECEDENTS:
            precedents.append({
                'category': category,
                'relevance': 'high',
                **LEGAL_PRECEDENTS[category]
            })

    return precedents


def calculate_risk_score(risks: List[Dict], missing_clauses: List[str]) -> int:
    """
    Calculate overall risk score (0-100)
    """
    score = 0

    # Add points for each identified risk
    for risk in risks:
        if risk['severity'] == 'HIGH':
            score += 25
        elif risk['severity'] == 'MEDIUM':
            score += 15
        else:
            score += 5

    # Add points for missing critical clauses
    score += len(missing_clauses) * 10

    # Cap at 100
    return min(score, 100)


def get_risk_level(score: int) -> str:
    """
    Convert numeric score to risk level
    """
    if score >= 70:
        return 'CRITICAL'
    elif score >= 50:
        return 'HIGH'
    elif score >= 30:
        return 'MEDIUM'
    else:
        return 'LOW'


def generate_recommendations(risks: List[Dict], missing_clauses: List[str]) -> List[str]:
    """
    Generate actionable recommendations
    """
    recommendations = []

    for risk in risks:
        recommendations.append(f"⚠️ {risk['description']}: {risk['recommendation']}")

    if missing_clauses:
        recommendations.append(
            f"📋 Add the following critical clauses: {', '.join(missing_clauses)}"
        )

    if not recommendations:
        recommendations.append("✅ Document appears to have standard protections")

    return recommendations


def get_html_ui() -> str:
    """
    Generate web UI for the legal document analyzer
    """
    # Try to read from external file first
    try:
        import os
        # Check if index.html exists in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'index.html')

        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Could not read index.html: {e}")

    # Fallback HTML with fixed JavaScript
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Document Analysis Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        h1 { color: #1e3c72; margin-bottom: 10px; font-size: 2em; }
        .subtitle { color: #666; font-size: 1.1em; }
        .main-section { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        h2 { color: #1e3c72; margin-bottom: 20px; }
        .input-area { margin-bottom: 20px; }
        textarea { width: 100%; min-height: 300px; padding: 15px; border: 2px solid #1e3c72; border-radius: 10px; font-family: 'Courier New', monospace; font-size: 14px; resize: vertical; }
        textarea:focus { outline: none; border-color: #2a5298; box-shadow: 0 0 10px rgba(30, 60, 114, 0.3); }
        .button-group { display: flex; gap: 15px; margin-top: 15px; }
        button { background: #1e3c72; color: white; padding: 12px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; transition: all 0.3s; }
        button:hover { background: #2a5298; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        button:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .results { display: none; margin-top: 30px; }
        .results.active { display: block; }
        .risk-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin: 10px 0; }
        .risk-CRITICAL { background: #dc3545; color: white; }
        .risk-HIGH { background: #fd7e14; color: white; }
        .risk-MEDIUM { background: #ffc107; color: #000; }
        .risk-LOW { background: #28a745; color: white; }
        .loading { display: none; text-align: center; padding: 20px; color: #1e3c72; }
        .loading.active { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #1e3c72; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ Legal Document Analysis Agent</h1>
            <p class="subtitle">AI-Powered Contract Review & Risk Assessment</p>
        </div>
        <div class="main-section">
            <h2>Document Analysis</h2>
            <div class="input-area">
                <label for="document-text"><strong>Paste your legal document or contract below:</strong></label>
                <textarea id="document-text" placeholder="Enter the contract text here..."></textarea>
            </div>
            <div class="button-group">
                <button onclick="analyzeDocument()">📊 Analyze Document</button>
                <button onclick="clearResults()">🔄 Clear</button>
            </div>
            <div class="loading" id="loading"><div class="spinner"></div><p>Analyzing document with AI...</p></div>
            <div class="results" id="results"><h2>Analysis Results</h2><div id="results-content"></div></div>
        </div>
    </div>
    <script>
        console.log("Script loading...");
        function analyzeDocument() { alert("Function works!"); }
        function clearResults() { document.getElementById("document-text").value = ""; document.getElementById("results").classList.remove("active"); }
        console.log("Script loaded!");
    </script>
</body>
</html>'''


if __name__ == "__main__":
    # Test locally
    test_event = {
        'httpMethod': 'GET',
        'path': '/'
    }
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
