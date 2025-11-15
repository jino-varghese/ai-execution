"""
FastAPI REST API for Medical Diagnosis System
Provides endpoints for healthcare professionals to interact with the AI agent.
"""

import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import yaml
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.medical_diagnosis_agent import (
    MedicalDiagnosisAgent,
    PatientData,
    DiagnosisResult
)
from rag.medical_rag import MedicalRAG
from preprocessing.data_processor import MedicalDataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Medical Diagnosis System",
    description="AI-powered medical diagnosis and treatment recommendations for healthcare professionals",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Load configuration
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize components
diagnosis_agent = None
rag_system = None


# Pydantic models for API
class PatientRequest(BaseModel):
    """Patient information request model"""
    patient_id: str = Field(..., description="Unique patient identifier")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    gender: str = Field(..., description="Patient gender")
    symptoms: List[str] = Field(..., min_items=1, description="List of symptoms")
    medical_history: List[str] = Field(default=[], description="Medical history")
    current_medications: List[str] = Field(default=[], description="Current medications")
    allergies: List[str] = Field(default=[], description="Known allergies")
    vital_signs: Optional[dict] = Field(None, description="Vital signs measurements")
    lab_results: Optional[dict] = Field(None, description="Laboratory results")

    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PT12345",
                "age": 45,
                "gender": "male",
                "symptoms": [
                    "chest pain for 2 hours",
                    "shortness of breath",
                    "sweating"
                ],
                "medical_history": ["hypertension", "high cholesterol"],
                "current_medications": ["lisinopril", "atorvastatin"],
                "allergies": ["penicillin"],
                "vital_signs": {
                    "blood_pressure": "150/95",
                    "heart_rate": 98,
                    "temperature": 37.2
                }
            }
        }


class DiagnosisResponse(BaseModel):
    """Diagnosis response model"""
    diagnosis_id: str
    patient_id: str
    potential_diagnoses: List[dict]
    recommended_tests: List[str]
    treatment_recommendations: List[dict]
    confidence_score: float
    supporting_evidence: List[str]
    warnings: List[str]
    timestamp: str
    requires_review: bool


class ConsultationRequest(BaseModel):
    """Consultation request model"""
    patient_request: PatientRequest
    query: str = Field(..., description="Specific medical question")


class KnowledgeSearchRequest(BaseModel):
    """Knowledge search request model"""
    query: str = Field(..., description="Search query")
    source_types: Optional[List[str]] = Field(
        None,
        description="Knowledge sources to search (medical_literature, drug_databases, clinical_trials)"
    )
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results")


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global diagnosis_agent, rag_system

    logger.info("Initializing AI Medical Diagnosis System...")

    try:
        # Initialize RAG system
        rag_system = MedicalRAG(config['rag'])
        logger.info("RAG system initialized")

        # Initialize diagnosis agent
        diagnosis_agent = MedicalDiagnosisAgent(config)
        logger.info("Medical Diagnosis Agent initialized")

        logger.info("System initialization complete")

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Medical Diagnosis System",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "diagnosis": "/api/v1/diagnosis",
            "consultation": "/api/v1/consultation",
            "knowledge_search": "/api/v1/knowledge/search",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "diagnosis_agent": diagnosis_agent is not None,
            "rag_system": rag_system is not None
        }
    }


@app.post("/api/v1/diagnosis", response_model=DiagnosisResponse)
async def get_diagnosis(
    patient_request: PatientRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate AI-powered diagnosis and treatment recommendations.

    This endpoint requires authentication and is intended for use by
    licensed healthcare professionals only.
    """
    logger.info(f"Diagnosis request for patient {patient_request.patient_id}")

    try:
        # Convert request to PatientData
        patient_data = PatientData(
            patient_id=patient_request.patient_id,
            age=patient_request.age,
            gender=patient_request.gender,
            symptoms=patient_request.symptoms,
            medical_history=patient_request.medical_history,
            current_medications=patient_request.current_medications,
            allergies=patient_request.allergies,
            vital_signs=patient_request.vital_signs,
            lab_results=patient_request.lab_results
        )

        # Get diagnosis from agent
        diagnosis_result = diagnosis_agent.diagnose(patient_data)

        # Convert to response model
        response = DiagnosisResponse(
            diagnosis_id=diagnosis_result.diagnosis_id,
            patient_id=diagnosis_result.patient_id,
            potential_diagnoses=diagnosis_result.potential_diagnoses,
            recommended_tests=diagnosis_result.recommended_tests,
            treatment_recommendations=diagnosis_result.treatment_recommendations,
            confidence_score=diagnosis_result.confidence_score,
            supporting_evidence=diagnosis_result.supporting_evidence,
            warnings=diagnosis_result.warnings,
            timestamp=diagnosis_result.timestamp,
            requires_review=diagnosis_result.requires_review
        )

        logger.info(f"Diagnosis completed for patient {patient_request.patient_id}")
        return response

    except Exception as e:
        logger.error(f"Error processing diagnosis request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing diagnosis: {str(e)}"
        )


@app.post("/api/v1/consultation")
async def get_consultation(
    consultation_request: ConsultationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get real-time consultation for specific medical questions.

    Provides expert AI assistance for specific medical queries in the context
    of a patient case.
    """
    logger.info(f"Consultation request for patient {consultation_request.patient_request.patient_id}")

    try:
        # Convert request to PatientData
        patient_data = PatientData(
            patient_id=consultation_request.patient_request.patient_id,
            age=consultation_request.patient_request.age,
            gender=consultation_request.patient_request.gender,
            symptoms=consultation_request.patient_request.symptoms,
            medical_history=consultation_request.patient_request.medical_history,
            current_medications=consultation_request.patient_request.current_medications,
            allergies=consultation_request.patient_request.allergies,
            vital_signs=consultation_request.patient_request.vital_signs,
            lab_results=consultation_request.patient_request.lab_results
        )

        # Get consultation response
        response = diagnosis_agent.get_consultation(
            patient_data,
            consultation_request.query
        )

        return {
            "patient_id": patient_data.patient_id,
            "query": consultation_request.query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This AI-generated response must be reviewed by a licensed healthcare professional"
        }

    except Exception as e:
        logger.error(f"Error processing consultation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing consultation: {str(e)}"
        )


@app.post("/api/v1/knowledge/search")
async def search_knowledge(
    search_request: KnowledgeSearchRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Search medical knowledge base including literature, drug databases, and clinical trials.
    """
    logger.info(f"Knowledge search request: {search_request.query}")

    try:
        results = rag_system.retrieve(
            query=search_request.query,
            source_names=search_request.source_types,
            top_k=search_request.top_k
        )

        return {
            "query": search_request.query,
            "results": results,
            "total_results": len(results),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing knowledge search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search: {str(e)}"
        )


@app.get("/api/v1/drug/{drug_name}")
async def get_drug_info(
    drug_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed drug information including interactions and contraindications"""
    logger.info(f"Drug information request: {drug_name}")

    try:
        drug_info = rag_system.search_drug_database(drug_name)

        return {
            "drug_name": drug_name,
            "information": drug_info,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving drug information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving drug information: {str(e)}"
        )


@app.get("/api/v1/clinical-trials/{condition}")
async def search_clinical_trials(
    condition: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Search for relevant clinical trials for a medical condition"""
    logger.info(f"Clinical trials search: {condition}")

    try:
        trials = rag_system.search_clinical_trials(condition)

        return {
            "condition": condition,
            "trials": trials,
            "total_trials": len(trials),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching clinical trials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching clinical trials: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config['api']['host'],
        port=config['api']['port'],
        log_level="info"
    )
