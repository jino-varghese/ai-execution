"""
Medical NLP Processing Utilities
Handles medical terminology extraction and analysis.
"""

import logging
from typing import List, Dict, Set
import re

logger = logging.getLogger(__name__)


class MedicalNLPProcessor:
    """
    Processes medical text to extract entities and terminology.
    Note: In production, this would use scispacy or similar specialized libraries.
    """

    def __init__(self):
        """Initialize medical NLP processor"""
        # Common medical symptom keywords
        self.symptom_keywords = {
            'pain', 'fever', 'nausea', 'vomiting', 'headache', 'fatigue',
            'cough', 'shortness of breath', 'dizziness', 'weakness',
            'chest pain', 'abdominal pain', 'rash', 'swelling'
        }

        # Medical condition patterns
        self.condition_patterns = [
            r'\b(diabetes|hypertension|asthma|copd|cancer)\b',
            r'\b(heart disease|kidney disease|liver disease)\b',
        ]

        logger.info("Medical NLP Processor initialized")

    def analyze_symptoms(self, symptoms: List[str]) -> Dict:
        """
        Analyze patient symptoms to extract medical entities.

        Args:
            symptoms: List of symptom descriptions

        Returns:
            Dictionary with extracted medical information
        """
        analysis = {
            'primary_symptoms': [],
            'severity_indicators': [],
            'duration_mentions': [],
            'extracted_entities': []
        }

        for symptom in symptoms:
            symptom_lower = symptom.lower()

            # Extract severity
            if any(word in symptom_lower for word in ['severe', 'extreme', 'acute']):
                analysis['severity_indicators'].append('severe')
            elif any(word in symptom_lower for word in ['mild', 'slight']):
                analysis['severity_indicators'].append('mild')

            # Extract duration
            duration_match = re.search(r'(\d+)\s*(day|week|month|hour)', symptom_lower)
            if duration_match:
                analysis['duration_mentions'].append(duration_match.group(0))

            # Extract primary symptom
            for keyword in self.symptom_keywords:
                if keyword in symptom_lower:
                    analysis['primary_symptoms'].append(keyword)

        return analysis

    def extract_medical_conditions(self, text: str) -> List[str]:
        """
        Extract medical conditions from text.

        Args:
            text: Medical text

        Returns:
            List of extracted conditions
        """
        conditions = []

        for pattern in self.condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend(matches)

        return list(set(conditions))

    def normalize_medical_term(self, term: str) -> str:
        """
        Normalize medical terminology.

        Args:
            term: Medical term

        Returns:
            Normalized term
        """
        # Basic normalization (in production, use medical ontologies)
        normalized = term.lower().strip()

        # Common abbreviation expansions
        abbreviations = {
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'mi': 'myocardial infarction',
            'copd': 'chronic obstructive pulmonary disease',
        }

        return abbreviations.get(normalized, normalized)

    def extract_medications(self, text: str) -> List[str]:
        """
        Extract medication names from text.

        Args:
            text: Text containing medication information

        Returns:
            List of medication names
        """
        # Simplified medication extraction
        # In production, use RxNorm or similar drug databases
        medications = []

        # Common medication patterns
        medication_patterns = [
            r'\b([A-Z][a-z]+(?:in|ol|am|ide|one))\b',  # Common drug suffixes
        ]

        for pattern in medication_patterns:
            matches = re.findall(pattern, text)
            medications.extend(matches)

        return list(set(medications))
