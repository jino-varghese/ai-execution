"""
Data Preprocessing Pipeline for Medical Datasets
Handles cleaning, formatting, and preparation of medical data for fine-tuning.
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class MedicalDataProcessor:
    """
    Processes various medical datasets for fine-tuning and RAG indexing.
    """

    def __init__(self, config: Dict):
        """
        Initialize the data processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.raw_data_path = Path("data/raw")
        self.processed_data_path = Path("data/processed")

        # Create directories if they don't exist
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

        logger.info("Medical Data Processor initialized")

    def process_patient_records(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Process patient records for training data.

        Args:
            input_file: Path to raw patient records (CSV/JSON)
            output_file: Path to save processed data

        Returns:
            Path to processed file
        """
        logger.info(f"Processing patient records from {input_file}")

        if output_file is None:
            output_file = self.processed_data_path / "patient_records.jsonl"

        # Load data
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.json'):
            df = pd.read_json(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file}")

        # Process and clean data
        processed_records = []

        for idx, row in df.iterrows():
            # Anonymize patient data (HIPAA compliance)
            anonymized_record = self._anonymize_patient_data(row.to_dict())

            # Format for fine-tuning
            training_example = self._format_for_training(anonymized_record)

            processed_records.append(training_example)

        # Save as JSONL
        with open(output_file, 'w') as f:
            for record in processed_records:
                f.write(json.dumps(record) + '\n')

        logger.info(f"Processed {len(processed_records)} patient records to {output_file}")
        return str(output_file)

    def process_medical_literature(
        self,
        input_directory: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Process medical literature and research papers.

        Args:
            input_directory: Directory containing medical papers (PDF, TXT)
            output_file: Path to save processed data

        Returns:
            Path to processed file
        """
        logger.info(f"Processing medical literature from {input_directory}")

        if output_file is None:
            output_file = self.processed_data_path / "medical_literature.jsonl"

        processed_docs = []

        # Process all documents in directory
        for file_path in Path(input_directory).rglob('*'):
            if file_path.suffix.lower() in ['.txt', '.pdf', '.md']:
                try:
                    content = self._extract_text_from_file(file_path)

                    # Extract key information
                    processed_doc = {
                        'source': str(file_path),
                        'content': content,
                        'metadata': self._extract_metadata(content),
                        'type': 'medical_literature'
                    }

                    processed_docs.append(processed_doc)

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

        # Save processed documents
        with open(output_file, 'w') as f:
            for doc in processed_docs:
                f.write(json.dumps(doc) + '\n')

        logger.info(f"Processed {len(processed_docs)} literature documents to {output_file}")
        return str(output_file)

    def process_treatment_protocols(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Process treatment protocols and clinical guidelines.

        Args:
            input_file: Path to treatment protocols file
            output_file: Path to save processed data

        Returns:
            Path to processed file
        """
        logger.info(f"Processing treatment protocols from {input_file}")

        if output_file is None:
            output_file = self.processed_data_path / "treatment_protocols.jsonl"

        # Load and process protocols
        with open(input_file, 'r') as f:
            protocols = json.load(f)

        processed_protocols = []

        for protocol in protocols:
            # Structure protocol for training
            formatted_protocol = {
                'condition': protocol.get('condition'),
                'protocol': protocol.get('protocol'),
                'evidence_level': protocol.get('evidence_level'),
                'references': protocol.get('references', []),
                'type': 'treatment_protocol'
            }

            processed_protocols.append(formatted_protocol)

        # Save processed protocols
        with open(output_file, 'w') as f:
            for protocol in processed_protocols:
                f.write(json.dumps(protocol) + '\n')

        logger.info(f"Processed {len(processed_protocols)} protocols to {output_file}")
        return str(output_file)

    def create_fine_tuning_dataset(
        self,
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a comprehensive fine-tuning dataset from all processed data.

        Args:
            output_file: Path to save fine-tuning dataset

        Returns:
            Path to fine-tuning dataset
        """
        logger.info("Creating fine-tuning dataset")

        if output_file is None:
            output_file = self.processed_data_path / "fine_tuning_dataset.jsonl"

        # Combine all processed data sources
        all_data = []

        # Load patient records
        patient_records_file = self.processed_data_path / "patient_records.jsonl"
        if patient_records_file.exists():
            with open(patient_records_file, 'r') as f:
                all_data.extend([json.loads(line) for line in f])

        # Load medical literature
        literature_file = self.processed_data_path / "medical_literature.jsonl"
        if literature_file.exists():
            with open(literature_file, 'r') as f:
                all_data.extend([json.loads(line) for line in f])

        # Load treatment protocols
        protocols_file = self.processed_data_path / "treatment_protocols.jsonl"
        if protocols_file.exists():
            with open(protocols_file, 'r') as f:
                all_data.extend([json.loads(line) for line in f])

        # Save combined dataset
        with open(output_file, 'w') as f:
            for item in all_data:
                f.write(json.dumps(item) + '\n')

        logger.info(f"Created fine-tuning dataset with {len(all_data)} examples at {output_file}")
        return str(output_file)

    def _anonymize_patient_data(self, record: Dict) -> Dict:
        """
        Anonymize patient data for HIPAA compliance.

        Args:
            record: Patient record dictionary

        Returns:
            Anonymized record
        """
        # Remove or hash identifying information
        anonymized = record.copy()

        # Remove PII fields
        pii_fields = ['name', 'ssn', 'address', 'phone', 'email']
        for field in pii_fields:
            if field in anonymized:
                del anonymized[field]

        # Replace patient ID with anonymized ID
        if 'patient_id' in anonymized:
            anonymized['patient_id'] = f"ANON_{hash(anonymized['patient_id']) % 1000000}"

        return anonymized

    def _format_for_training(self, record: Dict) -> Dict:
        """
        Format record for LLM fine-tuning (instruction-response pairs).

        Args:
            record: Patient record

        Returns:
            Formatted training example
        """
        # Create instruction-response pair
        instruction = self._create_instruction_from_record(record)
        response = self._create_response_from_record(record)

        return {
            'instruction': instruction,
            'response': response,
            'metadata': {
                'source': 'patient_records',
                'patient_id': record.get('patient_id')
            }
        }

    def _create_instruction_from_record(self, record: Dict) -> str:
        """Create instruction text from patient record"""
        parts = ["Patient Case:"]

        if 'age' in record and 'gender' in record:
            parts.append(f"- {record['age']} year old {record['gender']}")

        if 'symptoms' in record:
            parts.append(f"- Symptoms: {', '.join(record['symptoms'])}")

        if 'medical_history' in record:
            parts.append(f"- Medical History: {', '.join(record['medical_history'])}")

        parts.append("\nProvide potential diagnoses and treatment recommendations.")

        return "\n".join(parts)

    def _create_response_from_record(self, record: Dict) -> str:
        """Create response text from patient record"""
        parts = []

        if 'diagnosis' in record:
            parts.append(f"Diagnosis: {record['diagnosis']}")

        if 'treatment' in record:
            parts.append(f"Treatment: {record['treatment']}")

        if 'notes' in record:
            parts.append(f"Notes: {record['notes']}")

        return "\n".join(parts)

    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text content from various file formats"""
        if file_path.suffix.lower() == '.txt' or file_path.suffix.lower() == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.suffix.lower() == '.pdf':
            # Would use PyPDF2 or similar library
            logger.warning(f"PDF parsing not fully implemented for {file_path}")
            return ""
        else:
            return ""

    def _extract_metadata(self, content: str) -> Dict:
        """Extract metadata from document content"""
        metadata = {}

        # Extract title (first line or heading)
        lines = content.split('\n')
        if lines:
            metadata['title'] = lines[0].strip()

        # Extract keywords (simplified - would use NLP in production)
        metadata['length'] = len(content)

        return metadata

    def validate_dataset(self, dataset_path: str) -> Dict:
        """
        Validate a processed dataset.

        Args:
            dataset_path: Path to dataset file

        Returns:
            Validation report
        """
        logger.info(f"Validating dataset {dataset_path}")

        validation_report = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'errors': []
        }

        with open(dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                validation_report['total_records'] += 1
                try:
                    record = json.loads(line)
                    # Basic validation
                    if 'instruction' in record or 'content' in record:
                        validation_report['valid_records'] += 1
                    else:
                        validation_report['invalid_records'] += 1
                        validation_report['errors'].append(
                            f"Line {line_num}: Missing required fields"
                        )
                except json.JSONDecodeError as e:
                    validation_report['invalid_records'] += 1
                    validation_report['errors'].append(
                        f"Line {line_num}: JSON decode error - {str(e)}"
                    )

        logger.info(f"Validation complete: {validation_report['valid_records']}/{validation_report['total_records']} valid")
        return validation_report
