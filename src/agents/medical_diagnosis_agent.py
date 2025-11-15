"""
Medical Diagnosis Agent
Provides AI-powered diagnosis and treatment recommendations for healthcare professionals.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# LLM imports
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# Local imports
from src.rag.medical_rag import MedicalRAG
from src.utils.safety_checks import SafetyValidator
from src.utils.medical_terminology import MedicalNLPProcessor

logger = logging.getLogger(__name__)


@dataclass
class PatientData:
    """Patient information structure"""
    patient_id: str
    age: int
    gender: str
    symptoms: List[str]
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    vital_signs: Optional[Dict[str, float]] = None
    lab_results: Optional[Dict[str, str]] = None


@dataclass
class DiagnosisResult:
    """Diagnosis result structure"""
    diagnosis_id: str
    patient_id: str
    potential_diagnoses: List[Dict[str, any]]
    recommended_tests: List[str]
    treatment_recommendations: List[Dict[str, any]]
    confidence_score: float
    supporting_evidence: List[str]
    warnings: List[str]
    timestamp: str
    requires_review: bool


class MedicalDiagnosisAgent:
    """
    AI-powered medical diagnosis agent that assists healthcare professionals
    with diagnosis and treatment recommendations.
    """

    def __init__(self, config: Dict):
        """
        Initialize the medical diagnosis agent.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rag_system = MedicalRAG(config['rag'])
        self.safety_validator = SafetyValidator()
        self.nlp_processor = MedicalNLPProcessor()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=config['llm']['model_name'],
            temperature=config['llm']['temperature'],
            max_tokens=config['llm']['max_tokens']
        )

        # Setup agent tools
        self.tools = self._setup_tools()

        # Setup agent
        self.agent = self._setup_agent()

        logger.info("Medical Diagnosis Agent initialized successfully")

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the agent to use"""
        tools = [
            Tool(
                name="RetrieveMedicalKnowledge",
                func=self.rag_system.retrieve,
                description="Retrieve relevant medical literature, research papers, and clinical guidelines"
            ),
            Tool(
                name="SearchDrugDatabase",
                func=self.rag_system.search_drug_database,
                description="Search drug interactions, contraindications, and dosage information"
            ),
            Tool(
                name="FindClinicalTrials",
                func=self.rag_system.search_clinical_trials,
                description="Find relevant clinical trials and latest treatment protocols"
            ),
            Tool(
                name="AnalyzeSymptoms",
                func=self.nlp_processor.analyze_symptoms,
                description="Analyze patient symptoms and extract medical entities"
            ),
            Tool(
                name="CheckDrugInteractions",
                func=self._check_drug_interactions,
                description="Check for potential drug interactions with current medications"
            )
        ]
        return tools

    def _setup_agent(self) -> AgentExecutor:
        """Setup the diagnosis agent with prompt and tools"""

        system_message = """You are an expert medical AI assistant designed to help healthcare professionals
        with diagnosis and treatment recommendations. You have access to:

        1. Medical literature and research papers
        2. Drug databases with interaction information
        3. Clinical trial data
        4. Treatment protocols and guidelines

        IMPORTANT GUIDELINES:
        - Always prioritize patient safety
        - Provide evidence-based recommendations with citations
        - Clearly state confidence levels
        - Flag cases requiring immediate attention
        - Consider differential diagnoses
        - Check for drug interactions and contraindications
        - Respect patient allergies and medical history

        Your role is to ASSIST healthcare professionals, not replace them.
        All recommendations should be reviewed by qualified medical personnel.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            max_iterations=self.config['agent']['max_iterations']
        )

        return agent_executor

    def diagnose(self, patient_data: PatientData) -> DiagnosisResult:
        """
        Generate diagnosis and treatment recommendations for a patient.

        Args:
            patient_data: Patient information and symptoms

        Returns:
            DiagnosisResult with diagnoses and recommendations
        """
        logger.info(f"Starting diagnosis for patient {patient_data.patient_id}")

        # Validate input
        self.safety_validator.validate_patient_data(patient_data)

        # Prepare input for agent
        input_text = self._prepare_diagnosis_input(patient_data)

        # Run agent
        try:
            response = self.agent.invoke({"input": input_text})

            # Parse and structure response
            diagnosis_result = self._parse_diagnosis_response(
                response['output'],
                patient_data
            )

            # Safety checks
            diagnosis_result = self.safety_validator.validate_diagnosis(
                diagnosis_result
            )

            logger.info(f"Diagnosis completed for patient {patient_data.patient_id}")
            return diagnosis_result

        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            raise

    def _prepare_diagnosis_input(self, patient_data: PatientData) -> str:
        """Prepare structured input for the diagnosis agent"""

        input_parts = [
            f"PATIENT CASE ANALYSIS",
            f"",
            f"Patient ID: {patient_data.patient_id}",
            f"Demographics: {patient_data.age} year old {patient_data.gender}",
            f"",
            f"Chief Complaints/Symptoms:",
        ]

        for symptom in patient_data.symptoms:
            input_parts.append(f"  - {symptom}")

        input_parts.append(f"\nMedical History:")
        for history in patient_data.medical_history:
            input_parts.append(f"  - {history}")

        if patient_data.current_medications:
            input_parts.append(f"\nCurrent Medications:")
            for med in patient_data.current_medications:
                input_parts.append(f"  - {med}")

        if patient_data.allergies:
            input_parts.append(f"\nAllergies:")
            for allergy in patient_data.allergies:
                input_parts.append(f"  - {allergy}")

        if patient_data.vital_signs:
            input_parts.append(f"\nVital Signs:")
            for key, value in patient_data.vital_signs.items():
                input_parts.append(f"  - {key}: {value}")

        input_parts.append(f"\nPlease provide:")
        input_parts.append(f"1. Differential diagnoses (ranked by likelihood)")
        input_parts.append(f"2. Recommended diagnostic tests")
        input_parts.append(f"3. Treatment recommendations with evidence")
        input_parts.append(f"4. Important warnings or red flags")

        return "\n".join(input_parts)

    def _parse_diagnosis_response(
        self,
        response: str,
        patient_data: PatientData
    ) -> DiagnosisResult:
        """Parse agent response into structured diagnosis result"""

        # This is a simplified parser - in production, use more sophisticated NLP
        diagnosis_result = DiagnosisResult(
            diagnosis_id=self._generate_diagnosis_id(),
            patient_id=patient_data.patient_id,
            potential_diagnoses=[],
            recommended_tests=[],
            treatment_recommendations=[],
            confidence_score=0.0,
            supporting_evidence=[],
            warnings=[],
            timestamp=datetime.now().isoformat(),
            requires_review=True
        )

        # Extract diagnoses, tests, treatments from response
        # This would use NLP to parse the structured response
        # For now, returning the structure with the full response
        diagnosis_result.supporting_evidence.append(response)

        return diagnosis_result

    def _check_drug_interactions(self, drugs: List[str]) -> Dict:
        """Check for drug interactions"""
        # This would interface with a drug interaction database
        return {
            "interactions": [],
            "warnings": []
        }

    def _generate_diagnosis_id(self) -> str:
        """Generate unique diagnosis ID"""
        return f"DX-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def get_consultation(
        self,
        patient_data: PatientData,
        query: str
    ) -> str:
        """
        Get real-time consultation for specific medical questions.

        Args:
            patient_data: Patient context
            query: Specific medical question

        Returns:
            Consultation response
        """
        context = self._prepare_diagnosis_input(patient_data)
        full_query = f"{context}\n\nSpecific Question: {query}"

        response = self.agent.invoke({"input": full_query})
        return response['output']
