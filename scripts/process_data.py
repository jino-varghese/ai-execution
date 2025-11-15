#!/usr/bin/env python
"""
Script to process medical datasets for training
"""

import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing.data_processor import MedicalDataProcessor


def main():
    """Process all medical datasets"""

    print("=" * 60)
    print("Medical Data Processing Pipeline")
    print("=" * 60)

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize processor
    processor = MedicalDataProcessor(config)

    # Process patient records
    print("\n[1/4] Processing patient records...")
    patient_records_path = Path("data/sample_data/sample_patient_records.json")
    if patient_records_path.exists():
        processor.process_patient_records(
            input_file=str(patient_records_path)
        )
        print("✓ Patient records processed")
    else:
        print("⚠ No patient records found, skipping...")

    # Process medical literature
    print("\n[2/4] Processing medical literature...")
    literature_path = Path("data/sample_data")
    if literature_path.exists():
        processor.process_medical_literature(
            input_directory=str(literature_path)
        )
        print("✓ Medical literature processed")
    else:
        print("⚠ No medical literature found, skipping...")

    # Create fine-tuning dataset
    print("\n[3/4] Creating fine-tuning dataset...")
    try:
        dataset_path = processor.create_fine_tuning_dataset()
        print(f"✓ Fine-tuning dataset created: {dataset_path}")
    except Exception as e:
        print(f"⚠ Error creating fine-tuning dataset: {e}")

    # Validate dataset
    print("\n[4/4] Validating dataset...")
    processed_path = Path("data/processed/fine_tuning_dataset.jsonl")
    if processed_path.exists():
        report = processor.validate_dataset(str(processed_path))
        print(f"\nValidation Report:")
        print(f"  Total records: {report['total_records']}")
        print(f"  Valid records: {report['valid_records']}")
        print(f"  Invalid records: {report['invalid_records']}")
        if report['errors']:
            print(f"  Errors: {len(report['errors'])}")

    print("\n" + "=" * 60)
    print("Data processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
