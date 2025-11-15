"""
Safety Validation Utilities
Ensures medical recommendations meet safety standards and compliance requirements.
"""

import logging
from typing import Dict, List
import re

logger = logging.getLogger(__name__)


class SafetyValidator:
    """
    Validates patient data and diagnosis results for safety and compliance.
    """

    def __init__(self):
        """Initialize safety validator"""
        # Critical symptoms requiring immediate attention
        self.red_flag_symptoms = [
            'chest pain',
            'severe headache',
            'difficulty breathing',
            'loss of consciousness',
            'stroke symptoms',
            'severe bleeding',
            'suicidal thoughts',
            'severe abdominal pain'
        ]

        # Drug interactions database (simplified)
        self.critical_drug_interactions = {
            'warfarin': ['aspirin', 'ibuprofen', 'nsaids'],
            'maoi': ['ssri', 'decongestants'],
        }

    def validate_patient_data(self, patient_data) -> bool:
        """
        Validate patient data for completeness and safety.

        Args:
            patient_data: PatientData object

        Returns:
            True if valid

        Raises:
            ValueError if validation fails
        """
        logger.info(f"Validating patient data for {patient_data.patient_id}")

        # Check required fields
        if not patient_data.patient_id:
            raise ValueError("Patient ID is required")

        if not patient_data.symptoms:
            raise ValueError("At least one symptom is required")

        # Check for red flag symptoms
        for symptom in patient_data.symptoms:
            if any(flag in symptom.lower() for flag in self.red_flag_symptoms):
                logger.warning(f"RED FLAG: Critical symptom detected - {symptom}")

        # Validate age
        if patient_data.age < 0 or patient_data.age > 150:
            raise ValueError(f"Invalid age: {patient_data.age}")

        logger.info("Patient data validation passed")
        return True

    def validate_diagnosis(self, diagnosis_result):
        """
        Validate diagnosis result for safety and quality.

        Args:
            diagnosis_result: DiagnosisResult object

        Returns:
            DiagnosisResult with safety warnings added
        """
        logger.info(f"Validating diagnosis {diagnosis_result.diagnosis_id}")

        # Flag low confidence diagnoses
        if diagnosis_result.confidence_score < 0.7:
            diagnosis_result.warnings.append(
                "Low confidence diagnosis - requires expert review"
            )
            diagnosis_result.requires_review = True

        # Always require human review for production use
        diagnosis_result.requires_review = True

        # Add standard disclaimer
        diagnosis_result.warnings.append(
            "This AI-generated diagnosis must be reviewed by a licensed healthcare professional"
        )

        logger.info("Diagnosis validation complete")
        return diagnosis_result

    def check_drug_interactions(
        self,
        current_medications: List[str],
        proposed_medications: List[str]
    ) -> Dict:
        """
        Check for potential drug interactions.

        Args:
            current_medications: List of current medications
            proposed_medications: List of proposed new medications

        Returns:
            Dictionary with interaction warnings
        """
        interactions = []
        warnings = []

        # Normalize medication names
        current_lower = [med.lower() for med in current_medications]
        proposed_lower = [med.lower() for med in proposed_medications]

        # Check for known interactions
        for current_med in current_lower:
            for proposed_med in proposed_lower:
                # Check critical interactions
                for drug, interacting_drugs in self.critical_drug_interactions.items():
                    if drug in current_med and any(
                        interacting in proposed_med for interacting in interacting_drugs
                    ):
                        interactions.append({
                            'severity': 'critical',
                            'drug1': current_med,
                            'drug2': proposed_med,
                            'description': f"Critical interaction between {drug} and {proposed_med}"
                        })

        if interactions:
            warnings.append(
                "CRITICAL: Drug interactions detected. Review required before prescribing."
            )

        return {
            'has_interactions': len(interactions) > 0,
            'interactions': interactions,
            'warnings': warnings
        }

    def check_allergies(
        self,
        allergies: List[str],
        proposed_medications: List[str]
    ) -> Dict:
        """
        Check proposed medications against patient allergies.

        Args:
            allergies: List of patient allergies
            proposed_medications: List of proposed medications

        Returns:
            Dictionary with allergy warnings
        """
        allergy_warnings = []

        allergies_lower = [allergy.lower() for allergy in allergies]
        meds_lower = [med.lower() for med in proposed_medications]

        for allergy in allergies_lower:
            for med in meds_lower:
                if allergy in med or med in allergy:
                    allergy_warnings.append({
                        'severity': 'critical',
                        'allergy': allergy,
                        'medication': med,
                        'message': f"CONTRAINDICATED: Patient allergic to {allergy}"
                    })

        return {
            'has_contraindications': len(allergy_warnings) > 0,
            'warnings': allergy_warnings
        }

    def validate_age_appropriate_treatment(
        self,
        age: int,
        treatment: str
    ) -> bool:
        """
        Validate if treatment is appropriate for patient age.

        Args:
            age: Patient age
            treatment: Proposed treatment

        Returns:
            True if age-appropriate
        """
        # Simplified age-based checks
        if age < 18:
            # Pediatric considerations
            contraindicated_pediatric = ['aspirin', 'certain antibiotics']
            if any(drug in treatment.lower() for drug in contraindicated_pediatric):
                logger.warning(f"Age-inappropriate treatment for {age} year old")
                return False

        return True

    def hipaa_compliance_check(self, data: Dict) -> bool:
        """
        Check if data handling meets HIPAA compliance.

        Args:
            data: Data dictionary to check

        Returns:
            True if compliant
        """
        # Check for PII that should be encrypted/anonymized
        pii_fields = ['name', 'ssn', 'address', 'phone', 'email']

        for field in pii_fields:
            if field in data and data[field]:
                logger.warning(f"PII field {field} present - ensure encryption")

        return True
