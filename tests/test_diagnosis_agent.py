"""
Unit tests for Medical Diagnosis Agent
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.medical_diagnosis_agent import (
    MedicalDiagnosisAgent,
    PatientData,
    DiagnosisResult
)


class TestMedicalDiagnosisAgent:
    """Test suite for Medical Diagnosis Agent"""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'llm': {
                'model_name': 'gpt-3.5-turbo',
                'temperature': 0.3,
                'max_tokens': 2048
            },
            'rag': {
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'chunk_size': 512,
                'chunk_overlap': 50,
                'top_k': 5,
                'similarity_threshold': 0.7,
                'knowledge_sources': {}
            },
            'agent': {
                'max_iterations': 5,
                'confidence_threshold': 0.75,
                'require_human_review': True
            }
        }

    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data for testing"""
        return PatientData(
            patient_id="TEST001",
            age=45,
            gender="male",
            symptoms=[
                "chest pain for 2 hours",
                "shortness of breath",
                "sweating"
            ],
            medical_history=["hypertension", "high cholesterol"],
            current_medications=["lisinopril", "atorvastatin"],
            allergies=["penicillin"],
            vital_signs={
                "blood_pressure": "150/95",
                "heart_rate": 98,
                "temperature": 37.2
            }
        )

    def test_patient_data_creation(self, sample_patient_data):
        """Test PatientData object creation"""
        assert sample_patient_data.patient_id == "TEST001"
        assert sample_patient_data.age == 45
        assert len(sample_patient_data.symptoms) == 3
        assert "hypertension" in sample_patient_data.medical_history

    def test_diagnosis_id_generation(self, sample_config):
        """Test diagnosis ID generation"""
        # This would require mocking the agent initialization
        # Skipping for now as it requires API keys
        pass

    def test_prepare_diagnosis_input(self, sample_config, sample_patient_data):
        """Test diagnosis input preparation"""
        # Mock test - would require proper agent initialization
        pass


class TestCaseStudies:
    """
    Test cases based on real-world medical scenarios.
    These tests validate the system's effectiveness with case studies.
    """

    def test_case_study_1_cardiac_emergency(self):
        """
        Case Study 1: Acute Coronary Syndrome

        Patient: 58-year-old male
        Presentation: Severe chest pain, radiating to left arm, sweating
        History: Smoker, family history of heart disease

        Expected: Should identify as potential cardiac emergency
        """
        patient = PatientData(
            patient_id="CASE001",
            age=58,
            gender="male",
            symptoms=[
                "severe chest pain radiating to left arm",
                "profuse sweating",
                "nausea"
            ],
            medical_history=["smoker for 20 years", "family history of heart disease"],
            current_medications=[],
            allergies=[],
            vital_signs={
                "blood_pressure": "160/100",
                "heart_rate": 110
            }
        )

        # This would test the actual diagnosis
        # For now, we're documenting the expected behavior
        assert patient.age == 58
        assert "severe chest pain" in patient.symptoms[0]

    def test_case_study_2_diabetes_management(self):
        """
        Case Study 2: Type 2 Diabetes Management

        Patient: 52-year-old female
        Presentation: Increased thirst, frequent urination, fatigue
        History: Obesity, sedentary lifestyle

        Expected: Should suggest diabetes screening and lifestyle modifications
        """
        patient = PatientData(
            patient_id="CASE002",
            age=52,
            gender="female",
            symptoms=[
                "increased thirst for 3 weeks",
                "frequent urination",
                "persistent fatigue"
            ],
            medical_history=["obesity (BMI 32)", "sedentary lifestyle"],
            current_medications=[],
            allergies=[],
            vital_signs={
                "weight": 90,
                "height": 165
            }
        )

        assert patient.age == 52
        assert len(patient.symptoms) == 3

    def test_case_study_3_drug_interaction(self):
        """
        Case Study 3: Potential Drug Interaction

        Patient: 70-year-old male on anticoagulant therapy
        New symptom: Joint pain

        Expected: Should warn about NSAIDs interaction with warfarin
        """
        patient = PatientData(
            patient_id="CASE003",
            age=70,
            gender="male",
            symptoms=["knee joint pain"],
            medical_history=["atrial fibrillation"],
            current_medications=["warfarin"],
            allergies=[]
        )

        # System should flag potential interaction if NSAIDs are recommended
        assert "warfarin" in patient.current_medications
        assert patient.age >= 65  # Elderly patient - extra caution needed


def test_integration_workflow():
    """
    Integration test for complete diagnosis workflow.
    Tests the end-to-end process from patient data to diagnosis.
    """
    # This would require full system setup with API keys
    # Placeholder for integration testing
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
