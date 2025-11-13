"""
AI-Powered Medical Diagnosis and Treatment Recommendations System
===================================================================

This Lambda function implements a simplified medical diagnosis system that:
1. Accepts patient symptoms from healthcare professionals
2. Uses AI algorithms to suggest potential diagnoses
3. Retrieves relevant medical knowledge using RAG (Retrieval-Augmented Generation)
4. Provides treatment recommendations

DISCLAIMER: This is an educational demo. NOT for actual medical use.
Always consult qualified healthcare professionals for medical advice.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================================
# MEDICAL KNOWLEDGE BASE (Simulated Training Data)
# ============================================================================
# This represents a simplified medical knowledge base that would normally
# come from fine-tuning an LLM on medical literature, patient records,
# and treatment protocols.

MEDICAL_KNOWLEDGE_BASE = {
    "diseases": [
        {
            "id": "flu",
            "name": "Influenza (Flu)",
            "symptoms": ["fever", "cough", "sore throat", "fatigue", "muscle aches", "headache", "chills"],
            "severity": "moderate",
            "description": "Viral infection affecting the respiratory system",
            "treatments": [
                "Rest and adequate sleep (7-9 hours)",
                "Drink plenty of fluids (water, herbal tea)",
                "Antiviral medications (Oseltamivir) if within 48 hours of symptom onset",
                "Over-the-counter pain relievers (Acetaminophen, Ibuprofen)",
                "Stay home to prevent spreading"
            ],
            "when_to_seek_emergency": "Difficulty breathing, chest pain, severe dizziness, or symptoms that improve then worsen"
        },
        {
            "id": "common_cold",
            "name": "Common Cold",
            "symptoms": ["runny nose", "sneezing", "cough", "sore throat", "mild headache", "congestion"],
            "severity": "mild",
            "description": "Viral infection of the upper respiratory tract",
            "treatments": [
                "Rest and stay hydrated",
                "Warm fluids (soup, tea with honey)",
                "Saline nasal drops or spray",
                "Over-the-counter decongestants",
                "Vitamin C supplements may reduce duration"
            ],
            "when_to_seek_emergency": "Symptoms lasting more than 10 days, high fever (>101.3°F), or severe sinus pain"
        },
        {
            "id": "hypertension",
            "name": "Hypertension (High Blood Pressure)",
            "symptoms": ["headache", "dizziness", "shortness of breath", "nosebleeds", "fatigue"],
            "severity": "moderate-high",
            "description": "Chronic condition where blood pressure is consistently elevated",
            "treatments": [
                "Lifestyle modifications: reduce sodium intake (<2,300mg/day)",
                "Regular exercise (150 minutes/week)",
                "ACE inhibitors or ARBs as prescribed",
                "Calcium channel blockers if needed",
                "Monitor blood pressure regularly",
                "Manage stress through meditation or yoga"
            ],
            "when_to_seek_emergency": "Blood pressure >180/120, severe headache, chest pain, or vision changes"
        },
        {
            "id": "diabetes_t2",
            "name": "Type 2 Diabetes",
            "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing wounds", "weight loss"],
            "severity": "high",
            "description": "Metabolic disorder characterized by high blood sugar levels",
            "treatments": [
                "Blood glucose monitoring (fasting and post-meal)",
                "Metformin as first-line medication",
                "Dietary changes: low glycemic index foods",
                "Regular physical activity (30 min/day)",
                "Weight management (5-10% reduction if overweight)",
                "HbA1c monitoring every 3 months"
            ],
            "when_to_seek_emergency": "Blood sugar >300 mg/dL, confusion, extreme thirst, or fruity breath odor"
        },
        {
            "id": "migraine",
            "name": "Migraine Headache",
            "symptoms": ["severe headache", "nausea", "vomiting", "sensitivity to light", "sensitivity to sound", "visual disturbances"],
            "severity": "moderate",
            "description": "Neurological condition causing intense, debilitating headaches",
            "treatments": [
                "Triptans (Sumatriptan, Rizatriptan) for acute attacks",
                "NSAIDs (Ibuprofen, Naproxen) for pain",
                "Preventive medications: Beta-blockers, Anticonvulsants",
                "Identify and avoid triggers (stress, certain foods)",
                "Rest in dark, quiet room",
                "Apply cold compress to head"
            ],
            "when_to_seek_emergency": "Sudden severe headache, fever with stiff neck, or headache after head injury"
        },
        {
            "id": "pneumonia",
            "name": "Pneumonia",
            "symptoms": ["fever", "cough", "chest pain", "shortness of breath", "fatigue", "chills", "sweating"],
            "severity": "high",
            "description": "Infection causing inflammation in the lungs",
            "treatments": [
                "Antibiotics (Amoxicillin, Azithromycin) for bacterial pneumonia",
                "Rest and increased fluid intake",
                "Oxygen therapy if oxygen levels are low",
                "Fever reducers and pain relievers",
                "Breathing exercises and incentive spirometry",
                "Hospitalization may be required for severe cases"
            ],
            "when_to_seek_emergency": "Difficulty breathing, blue lips or fingernails, confusion, or persistent chest pain"
        },
        {
            "id": "anxiety",
            "name": "Generalized Anxiety Disorder",
            "symptoms": ["excessive worry", "restlessness", "fatigue", "difficulty concentrating", "muscle tension", "sleep disturbances"],
            "severity": "moderate",
            "description": "Mental health condition characterized by persistent worry and anxiety",
            "treatments": [
                "Cognitive Behavioral Therapy (CBT)",
                "SSRIs (Sertraline, Escitalopram) as first-line medication",
                "Benzodiazepines for short-term relief (use cautiously)",
                "Mindfulness and relaxation techniques",
                "Regular exercise and sleep hygiene",
                "Limit caffeine and alcohol"
            ],
            "when_to_seek_emergency": "Suicidal thoughts, panic attacks, or inability to function in daily life"
        },
        {
            "id": "gastritis",
            "name": "Gastritis",
            "symptoms": ["abdominal pain", "nausea", "vomiting", "bloating", "loss of appetite", "indigestion"],
            "severity": "mild-moderate",
            "description": "Inflammation of the stomach lining",
            "treatments": [
                "Proton pump inhibitors (Omeprazole, Lansoprazole)",
                "H2 blockers (Ranitidine, Famotidine)",
                "Antacids for symptom relief",
                "Avoid NSAIDs, alcohol, and spicy foods",
                "Small, frequent meals",
                "Test and treat H. pylori if present"
            ],
            "when_to_seek_emergency": "Vomiting blood, black tarry stools, or severe abdominal pain"
        }
    ],

    # Medical research papers (simulated RAG knowledge base)
    "research_papers": [
        {
            "title": "Antiviral Treatment for Influenza: A Systematic Review",
            "summary": "Oseltamivir reduces duration of symptoms by 1 day when administered within 48 hours of onset.",
            "citation": "Journal of Infectious Diseases, 2024",
            "relevance": ["flu"]
        },
        {
            "title": "Hypertension Management Guidelines 2024",
            "summary": "Lifestyle modifications combined with pharmacotherapy achieve better outcomes than medication alone.",
            "citation": "American Heart Association, 2024",
            "relevance": ["hypertension"]
        },
        {
            "title": "Type 2 Diabetes: Metformin as First-Line Therapy",
            "summary": "Metformin shows superior glycemic control and cardiovascular benefits compared to other oral agents.",
            "citation": "Diabetes Care, 2024",
            "relevance": ["diabetes_t2"]
        },
        {
            "title": "Cognitive Behavioral Therapy for Anxiety Disorders",
            "summary": "CBT demonstrates 60-80% response rates in treating generalized anxiety disorder.",
            "citation": "Journal of Clinical Psychology, 2024",
            "relevance": ["anxiety"]
        },
        {
            "title": "Community-Acquired Pneumonia Treatment Protocols",
            "summary": "Early antibiotic administration within 4 hours reduces mortality by 15%.",
            "citation": "New England Journal of Medicine, 2024",
            "relevance": ["pneumonia"]
        }
    ]
}


# ============================================================================
# AI DIAGNOSIS ENGINE
# ============================================================================
# This simulates an LLM fine-tuned on medical data that can analyze symptoms
# and suggest potential diagnoses.

def calculate_symptom_match(patient_symptoms: List[str], disease_symptoms: List[str]) -> float:
    """
    Calculate how well patient symptoms match a disease's symptom profile.

    This function implements a simple matching algorithm that would be replaced
    by a fine-tuned LLM in production.

    Args:
        patient_symptoms: List of symptoms reported by patient
        disease_symptoms: List of symptoms associated with a disease

    Returns:
        Match score between 0 and 1 (higher is better match)
    """
    # Normalize symptoms (lowercase, remove extra spaces)
    patient_symptoms_normalized = [s.lower().strip() for s in patient_symptoms]
    disease_symptoms_normalized = [s.lower().strip() for s in disease_symptoms]

    # Count matching symptoms
    matches = 0
    for patient_symptom in patient_symptoms_normalized:
        for disease_symptom in disease_symptoms_normalized:
            # Check for exact match or partial match
            if patient_symptom in disease_symptom or disease_symptom in patient_symptom:
                matches += 1
                break

    # Calculate score (weighted by number of patient symptoms)
    if len(patient_symptoms) == 0:
        return 0.0

    # Score based on percentage of patient symptoms explained
    base_score = matches / len(patient_symptoms)

    # Bonus for matching multiple disease symptoms
    if len(disease_symptoms) > 0:
        disease_coverage = matches / len(disease_symptoms)
        base_score = (base_score + disease_coverage) / 2

    return base_score


def diagnose_patient(symptoms: List[str], patient_history: str = "") -> List[Dict]:
    """
    AI-powered diagnosis engine that analyzes patient symptoms.

    This simulates an LLM fine-tuned on medical literature. In production,
    this would call a model like Amazon Bedrock with medical fine-tuning.

    Args:
        symptoms: List of patient symptoms
        patient_history: Optional patient medical history

    Returns:
        List of potential diagnoses ranked by confidence
    """
    diagnoses = []

    # Analyze each disease in knowledge base
    for disease in MEDICAL_KNOWLEDGE_BASE["diseases"]:
        # Calculate symptom match score
        match_score = calculate_symptom_match(symptoms, disease["symptoms"])

        # Only include if there's a reasonable match (>20%)
        if match_score > 0.2:
            diagnoses.append({
                "disease": disease["name"],
                "disease_id": disease["id"],
                "confidence": round(match_score * 100, 1),  # Convert to percentage
                "matched_symptoms": [s for s in symptoms if any(ds in s.lower() or s.lower() in ds for ds in disease["symptoms"])],
                "description": disease["description"],
                "severity": disease["severity"],
                "treatments": disease["treatments"],
                "emergency_signs": disease["when_to_seek_emergency"]
            })

    # Sort by confidence (highest first)
    diagnoses.sort(key=lambda x: x["confidence"], reverse=True)

    return diagnoses


# ============================================================================
# RAG (RETRIEVAL-AUGMENTED GENERATION) SYSTEM
# ============================================================================
# This retrieves relevant medical research and clinical guidelines to support
# diagnosis and treatment recommendations.

def retrieve_relevant_research(disease_ids: List[str]) -> List[Dict]:
    """
    RAG system that retrieves relevant medical research papers.

    In production, this would query vector databases with embedded medical
    literature, drug databases, and clinical trial information.

    Args:
        disease_ids: List of disease IDs to find research for

    Returns:
        List of relevant research papers
    """
    relevant_papers = []

    for paper in MEDICAL_KNOWLEDGE_BASE["research_papers"]:
        # Check if paper is relevant to any of the diagnosed diseases
        if any(disease_id in paper["relevance"] for disease_id in disease_ids):
            relevant_papers.append({
                "title": paper["title"],
                "summary": paper["summary"],
                "citation": paper["citation"]
            })

    return relevant_papers


# ============================================================================
# CONSULTATION AGENT
# ============================================================================
# This agent provides an interface for healthcare professionals to interact
# with the AI system.

def generate_consultation_report(symptoms: List[str], patient_history: str = "") -> Dict:
    """
    Generate a comprehensive medical consultation report.

    This agent combines:
    - AI diagnosis from fine-tuned LLM
    - Research retrieval from RAG system
    - Treatment recommendations

    Args:
        symptoms: Patient symptoms
        patient_history: Patient medical history

    Returns:
        Complete consultation report
    """
    # Step 1: Get AI diagnosis
    diagnoses = diagnose_patient(symptoms, patient_history)

    # Step 2: Retrieve relevant research
    disease_ids = [d["disease_id"] for d in diagnoses[:3]]  # Top 3 diagnoses
    research = retrieve_relevant_research(disease_ids)

    # Step 3: Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "patient_symptoms": symptoms,
        "patient_history": patient_history,
        "diagnosis_count": len(diagnoses),
        "top_diagnoses": diagnoses[:3],  # Top 3 most likely
        "all_diagnoses": diagnoses,
        "supporting_research": research,
        "recommendation": generate_recommendation(diagnoses)
    }

    return report


def generate_recommendation(diagnoses: List[Dict]) -> str:
    """
    Generate clinical recommendation based on diagnoses.

    Args:
        diagnoses: List of potential diagnoses

    Returns:
        Clinical recommendation text
    """
    if not diagnoses:
        return "Unable to determine diagnosis. Please conduct thorough physical examination and order relevant diagnostic tests."

    top_diagnosis = diagnoses[0]
    confidence = top_diagnosis["confidence"]

    if confidence > 70:
        return f"High confidence in {top_diagnosis['disease']}. Recommend following treatment protocol. Monitor patient closely."
    elif confidence > 50:
        return f"Moderate confidence in {top_diagnosis['disease']}. Consider differential diagnosis. May need additional tests."
    else:
        return f"Multiple potential diagnoses identified. Recommend comprehensive diagnostic workup including lab tests and imaging."


# ============================================================================
# WEB INTERFACE (HTML/CSS/JavaScript)
# ============================================================================

def get_html_interface() -> str:
    """
    Generate the web-based interface for the medical diagnosis system.

    Returns:
        Complete HTML page with embedded CSS and JavaScript
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Medical Diagnosis System</title>
    <style>
        /* Global Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .disclaimer {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 30px;
            color: #856404;
            font-weight: bold;
            text-align: center;
        }

        /* Main Content */
        .content {
            padding: 30px;
        }

        .section {
            margin-bottom: 30px;
        }

        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }

        input[type="text"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            resize: vertical;
            min-height: 100px;
        }

        .hint {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }

        /* Symptom Tags */
        .symptom-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }

        .symptom-tag {
            background: #e8eaf6;
            color: #667eea;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }

        .symptom-tag:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }

        .symptom-tag.selected {
            background: #667eea;
            color: white;
            border-color: #764ba2;
        }

        /* Button */
        .btn-diagnose {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 30px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            font-weight: bold;
        }

        .btn-diagnose:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }

        .btn-diagnose:active {
            transform: translateY(-1px);
        }

        .btn-diagnose:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        /* Results */
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }

        .results.show {
            display: block;
            animation: slideDown 0.5s ease;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .diagnosis-card {
            background: white;
            border-left: 5px solid #667eea;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .diagnosis-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .diagnosis-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }

        .confidence-badge {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }

        .severity-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }

        .severity-mild {
            background: #d4edda;
            color: #155724;
        }

        .severity-moderate {
            background: #fff3cd;
            color: #856404;
        }

        .severity-high {
            background: #f8d7da;
            color: #721c24;
        }

        .matched-symptoms {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }

        .treatment-list {
            margin: 15px 0;
        }

        .treatment-list li {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }

        .treatment-list li:last-child {
            border-bottom: none;
        }

        .emergency-warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }

        .emergency-warning strong {
            color: #721c24;
        }

        .research-papers {
            margin-top: 20px;
        }

        .paper-card {
            background: white;
            border-left: 4px solid #764ba2;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
        }

        .paper-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }

        .paper-citation {
            font-style: italic;
            color: #666;
            font-size: 0.9em;
        }

        /* Loading Spinner */
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
            display: none;
        }

        .spinner.show {
            display: block;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .diagnosis-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .confidence-badge {
                margin-top: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏥 AI Medical Diagnosis System</h1>
            <p>Advanced AI-Powered Healthcare Assistant</p>
        </div>

        <!-- Disclaimer -->
        <div class="disclaimer">
            ⚠️ EDUCATIONAL DEMO ONLY - NOT FOR ACTUAL MEDICAL USE<br>
            Always consult qualified healthcare professionals for medical advice.
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Symptom Input Section -->
            <div class="section">
                <h2>📋 Patient Symptoms</h2>

                <div class="form-group">
                    <label for="symptoms-input">Enter patient symptoms (comma-separated):</label>
                    <input type="text" id="symptoms-input"
                           placeholder="e.g., fever, cough, headache, fatigue">
                    <div class="hint">Type symptoms and press Enter, or select from common symptoms below</div>
                </div>

                <div class="form-group">
                    <label>Common Symptoms (click to select):</label>
                    <div class="symptom-tags" id="symptom-tags">
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Fever</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Cough</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Headache</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Fatigue</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Sore Throat</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Muscle Aches</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Shortness of Breath</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Nausea</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Dizziness</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Chest Pain</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Abdominal Pain</div>
                        <div class="symptom-tag" onclick="toggleSymptom(this)">Runny Nose</div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="history-input">Patient Medical History (optional):</label>
                    <textarea id="history-input"
                              placeholder="e.g., Pre-existing conditions, medications, allergies..."></textarea>
                </div>

                <button class="btn-diagnose" onclick="getDiagnosis()">
                    🔍 Analyze & Diagnose
                </button>
            </div>

            <!-- Loading Spinner -->
            <div class="spinner" id="spinner"></div>

            <!-- Results Section -->
            <div class="results" id="results">
                <h2>🎯 Diagnosis Results</h2>
                <div id="results-content"></div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Powered by AI and AWS Lambda | © 2025 Medical AI Research</p>
            <p>Built using LLM Fine-Tuning + RAG Architecture</p>
        </div>
    </div>

    <script>
        // Toggle symptom selection
        function toggleSymptom(element) {
            element.classList.toggle('selected');
        }

        // Get selected symptoms from tags
        function getSelectedSymptoms() {
            const tags = document.querySelectorAll('.symptom-tag.selected');
            return Array.from(tags).map(tag => tag.textContent);
        }

        // Main diagnosis function
        async function getDiagnosis() {
            // Get symptoms from input and selected tags
            const inputSymptoms = document.getElementById('symptoms-input').value
                .split(',')
                .map(s => s.trim())
                .filter(s => s.length > 0);

            const selectedSymptoms = getSelectedSymptoms();
            const allSymptoms = [...new Set([...inputSymptoms, ...selectedSymptoms])];

            if (allSymptoms.length === 0) {
                alert('Please enter or select at least one symptom.');
                return;
            }

            // Get patient history
            const history = document.getElementById('history-input').value;

            // Show spinner
            document.getElementById('spinner').classList.add('show');
            document.getElementById('results').classList.remove('show');

            try {
                // Send POST request to Lambda
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        symptoms: allSymptoms,
                        patient_history: history
                    })
                });

                const data = await response.json();

                // Hide spinner
                document.getElementById('spinner').classList.remove('show');

                // Display results
                displayResults(data);

            } catch (error) {
                document.getElementById('spinner').classList.remove('show');
                alert('Error analyzing symptoms. Please try again.');
                console.error('Error:', error);
            }
        }

        // Display diagnosis results
        function displayResults(data) {
            const resultsContent = document.getElementById('results-content');

            if (!data.top_diagnoses || data.top_diagnoses.length === 0) {
                resultsContent.innerHTML = '<p>No matching diagnoses found. Please consult a healthcare professional.</p>';
                document.getElementById('results').classList.add('show');
                return;
            }

            let html = '';

            // Add patient symptoms summary
            html += `
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <strong>Patient Symptoms:</strong> ${data.patient_symptoms.join(', ')}
                    <br><br>
                    <strong>Clinical Recommendation:</strong> ${data.recommendation}
                </div>
            `;

            // Add top diagnoses
            data.top_diagnoses.forEach((diagnosis, index) => {
                const severityClass = diagnosis.severity.includes('high') ? 'severity-high' :
                                     diagnosis.severity.includes('moderate') ? 'severity-moderate' :
                                     'severity-mild';

                html += `
                    <div class="diagnosis-card">
                        <div class="diagnosis-header">
                            <div class="diagnosis-name">${index + 1}. ${diagnosis.disease}</div>
                            <div class="confidence-badge">${diagnosis.confidence}% Match</div>
                        </div>

                        <p>${diagnosis.description}</p>

                        <span class="severity-badge ${severityClass}">
                            Severity: ${diagnosis.severity}
                        </span>

                        <div class="matched-symptoms">
                            <strong>Matched Symptoms:</strong> ${diagnosis.matched_symptoms.join(', ')}
                        </div>

                        <h4 style="margin-top: 15px;">💊 Treatment Recommendations:</h4>
                        <ul class="treatment-list">
                            ${diagnosis.treatments.map(t => `<li>${t}</li>`).join('')}
                        </ul>

                        <div class="emergency-warning">
                            <strong>⚠️ Seek Emergency Care If:</strong><br>
                            ${diagnosis.emergency_signs}
                        </div>
                    </div>
                `;
            });

            // Add supporting research
            if (data.supporting_research && data.supporting_research.length > 0) {
                html += `
                    <div class="research-papers">
                        <h3 style="color: #764ba2; margin-bottom: 15px;">📚 Supporting Medical Research</h3>
                `;

                data.supporting_research.forEach(paper => {
                    html += `
                        <div class="paper-card">
                            <div class="paper-title">${paper.title}</div>
                            <p>${paper.summary}</p>
                            <div class="paper-citation">${paper.citation}</div>
                        </div>
                    `;
                });

                html += '</div>';
            }

            resultsContent.innerHTML = html;
            document.getElementById('results').classList.add('show');

            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }

        // Allow Enter key to submit
        document.getElementById('symptoms-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                getDiagnosis();
            }
        });
    </script>
</body>
</html>
    """


# ============================================================================
# AWS LAMBDA HANDLER
# ============================================================================

def lambda_handler(event, context):
    """
    Main AWS Lambda handler function.

    This function handles both GET and POST requests:
    - GET: Returns the HTML interface
    - POST: Processes symptoms and returns diagnosis

    Args:
        event: AWS Lambda event object containing request data
        context: AWS Lambda context object

    Returns:
        HTTP response with appropriate headers and body
    """

    # Get HTTP method
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')

    # Handle GET request - return HTML interface
    if http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': get_html_interface()
        }

    # Handle POST request - process diagnosis
    elif http_method == 'POST':
        try:
            # Parse request body
            body = json.loads(event.get('body', '{}'))
            symptoms = body.get('symptoms', [])
            patient_history = body.get('patient_history', '')

            # Generate consultation report
            report = generate_consultation_report(symptoms, patient_history)

            # Return diagnosis results
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(report)
            }

        except Exception as e:
            # Error handling
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': str(e),
                    'message': 'Error processing diagnosis request'
                })
            }

    # Handle OPTIONS request (CORS preflight)
    elif http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }

    # Unknown method
    else:
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
