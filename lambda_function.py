import json
import boto3
import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
s3_client = boto3.client('s3')

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

    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')

        if http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': get_html_ui()
            }

        elif http_method == 'POST':
            body = json.loads(event.get('body', '{}'))

            if 'document' in body:
                # Analyze document
                result = analyze_document(body)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(result)
                }
            elif 'text' in body:
                # Quick risk assessment
                result = quick_risk_assessment(body['text'])
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(result)
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No document or text provided'})
                }

        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
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

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        analysis = response_body['content'][0]['text']

        return {
            'summary': analysis,
            'model': 'claude-3-sonnet',
            'confidence': 'high'
        }

    except Exception as e:
        # Fallback analysis if Bedrock is not available
        return {
            'summary': f'LLM analysis unavailable: {str(e)}. Using pattern-based analysis only.',
            'model': 'fallback',
            'confidence': 'low'
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
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Document Analysis Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        h1 {
            color: #1e3c72;
            margin-bottom: 10px;
            font-size: 2em;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .main-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        h2 {
            color: #1e3c72;
            margin-bottom: 20px;
        }

        .input-area {
            margin-bottom: 20px;
        }

        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #1e3c72;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
        }

        textarea:focus {
            outline: none;
            border-color: #2a5298;
            box-shadow: 0 0 10px rgba(30, 60, 114, 0.3);
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }

        button {
            background: #1e3c72;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }

        button:hover {
            background: #2a5298;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .results {
            display: none;
            margin-top: 30px;
        }

        .results.active {
            display: block;
        }

        .risk-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }

        .risk-CRITICAL {
            background: #dc3545;
            color: white;
        }

        .risk-HIGH {
            background: #fd7e14;
            color: white;
        }

        .risk-MEDIUM {
            background: #ffc107;
            color: #000;
        }

        .risk-LOW {
            background: #28a745;
            color: white;
        }

        .risk-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
        }

        .risk-item.HIGH {
            border-left-color: #fd7e14;
        }

        .risk-item.MEDIUM {
            border-left-color: #ffc107;
        }

        .risk-item.LOW {
            border-left-color: #28a745;
        }

        .clause-item {
            background: #e7f3ff;
            padding: 10px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 3px solid #1e3c72;
        }

        .missing-clause {
            background: #fff3cd;
            padding: 8px 15px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 3px solid #ffc107;
        }

        .recommendation {
            background: #d4edda;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 3px solid #28a745;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #1e3c72;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1e3c72;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .feature-card h3 {
            color: white;
            margin-bottom: 10px;
        }

        .sample-contracts {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .sample-btn {
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 15px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .sample-btn:hover {
            background: #764ba2;
        }
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

            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🤖 LLM Analysis</h3>
                    <p>Powered by Claude AI for deep legal understanding</p>
                </div>
                <div class="feature-card">
                    <h3>📚 RAG System</h3>
                    <p>Retrieves relevant legal precedents and case law</p>
                </div>
                <div class="feature-card">
                    <h3>⚠️ Risk Detection</h3>
                    <p>Identifies potential legal risks and missing clauses</p>
                </div>
                <div class="feature-card">
                    <h3>💡 Recommendations</h3>
                    <p>Actionable insights to improve contracts</p>
                </div>
            </div>

            <div class="input-area">
                <label for="document-text"><strong>Paste your legal document or contract below:</strong></label>
                <textarea id="document-text" placeholder="Enter the contract text here...

Example: Employment Agreement, NDA, Service Agreement, etc."></textarea>

                <div class="sample-contracts">
                    <strong>Try a sample:</strong>
                    <button class="sample-btn" onclick="loadSample('nda')">NDA</button>
                    <button class="sample-btn" onclick="loadSample('service')">Service Agreement</button>
                    <button class="sample-btn" onclick="loadSample('employment')">Employment</button>
                </div>
            </div>

            <div class="button-group">
                <button onclick="analyzeDocument()">📊 Analyze Document</button>
                <button onclick="clearResults()">🔄 Clear</button>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing document with AI...</p>
            </div>

            <div class="results" id="results">
                <h2>Analysis Results</h2>
                <div id="results-content"></div>
            </div>
        </div>
    </div>

    <script>
        const SAMPLE_CONTRACTS = {
            nda: `NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into on [DATE] by and between Company A and Company B.

1. CONFIDENTIAL INFORMATION
The parties agree to share certain proprietary information for the purpose of evaluating a potential business relationship.

2. OBLIGATIONS
The receiving party shall hold all information in strict confidence and shall not disclose such information to third parties.

3. TERM
This Agreement shall remain in effect for a period of two (2) years from the date of execution.

4. NO WARRANTIES
All information is provided "as is" without any warranty.

IN WITNESS WHEREOF, the parties have executed this Agreement.`,

            service: `SERVICE AGREEMENT

This Service Agreement is entered into between Service Provider ("Provider") and Client.

1. SERVICES
Provider agrees to perform web development services as specified in attached Statement of Work.

2. PAYMENT
Client shall pay Provider $10,000 per month, due within 30 days of invoice.

3. INTELLECTUAL PROPERTY
All work product created by Provider shall become the sole property of Client upon full payment.

4. TERMINATION
Either party may terminate this agreement with 30 days written notice.

5. INDEMNIFICATION
Provider shall indemnify and hold harmless Client from any claims arising from Provider's negligence.

6. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.`,

            employment: `EMPLOYMENT AGREEMENT

This Employment Agreement is made between Employer Inc. and Employee.

1. POSITION
Employee is hired as Senior Software Engineer.

2. COMPENSATION
Base salary of $150,000 per year, payable bi-weekly.

3. BENEFITS
Employee is eligible for health insurance, 401k, and paid time off.

4. CONFIDENTIALITY
Employee agrees to maintain confidentiality of all proprietary information and trade secrets.

5. NON-COMPETE
Employee agrees not to compete with Employer for 2 years following termination within 50 miles.

6. TERMINATION
Employment is at-will and may be terminated by either party at any time.

7. INTELLECTUAL PROPERTY
All inventions and works created during employment belong to Employer.`
        };

        function loadSample(type) {
            document.getElementById('document-text').value = SAMPLE_CONTRACTS[type];
        }

        async function analyzeDocument() {
            const text = document.getElementById('document-text').value.trim();

            if (!text) {
                alert('Please enter a document to analyze');
                return;
            }

            // Show loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        document: text,
                        type: 'contract'
                    })
                });

                const data = await response.json();
                displayResults(data);

            } catch (error) {
                alert('Error analyzing document: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('active');
            }
        }

        function displayResults(data) {
            const resultsDiv = document.getElementById('results-content');

            let html = `
                <div style="margin-bottom: 20px;">
                    <h3>Overall Risk Assessment</h3>
                    <div class="risk-badge risk-${data.risk_level}">
                        Risk Level: ${data.risk_level} (Score: ${data.risk_score}/100)
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <h3>🤖 AI Analysis</h3>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; white-space: pre-wrap;">
                        ${data.llm_analysis.summary}
                    </div>
                </div>
            `;

            if (data.identified_risks.length > 0) {
                html += '<h3>⚠️ Identified Risks</h3>';
                data.identified_risks.forEach(risk => {
                    html += `
                        <div class="risk-item ${risk.severity}">
                            <strong>${risk.severity}:</strong> ${risk.description}<br>
                            <em>Recommendation: ${risk.recommendation}</em>
                        </div>
                    `;
                });
            }

            if (data.missing_critical_clauses.length > 0) {
                html += '<h3>📋 Missing Critical Clauses</h3>';
                data.missing_critical_clauses.forEach(clause => {
                    html += `<div class="missing-clause">❌ ${clause}</div>`;
                });
            }

            if (data.identified_clauses.length > 0) {
                html += '<h3>📄 Identified Clauses</h3>';
                data.identified_clauses.forEach(clause => {
                    html += `
                        <div class="clause-item">
                            <strong>${clause.category.replace(/_/g, ' ').toUpperCase()}</strong><br>
                            <small>${clause.context.substring(0, 200)}...</small>
                        </div>
                    `;
                });
            }

            if (data.relevant_precedents.length > 0) {
                html += '<h3>📚 Relevant Legal Precedents</h3>';
                data.relevant_precedents.forEach(prec => {
                    html += `
                        <div class="clause-item">
                            <strong>${prec.category.replace(/_/g, ' ').toUpperCase()}</strong>
                            (${prec.risk_level} Risk)<br>
                            ${prec.description}<br>
                            <em>Best Practice: ${prec.best_practice}</em>
                        </div>
                    `;
                });
            }

            if (data.recommendations.length > 0) {
                html += '<h3>💡 Recommendations</h3>';
                data.recommendations.forEach(rec => {
                    html += `<div class="recommendation">${rec}</div>`;
                });
            }

            resultsDiv.innerHTML = html;
            document.getElementById('results').classList.add('active');

            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }

        function clearResults() {
            document.getElementById('document-text').value = '';
            document.getElementById('results').classList.remove('active');
        }
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    # Test locally
    test_event = {
        'httpMethod': 'GET',
        'path': '/'
    }
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
