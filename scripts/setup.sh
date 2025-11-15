#!/bin/bash

# Setup script for AI Medical Diagnosis System

echo "=========================================="
echo "AI Medical Diagnosis System - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p data/{raw,processed,medical_literature,drug_databases,clinical_trials}
mkdir -p models/fine_tuned
mkdir -p logs
mkdir -p data/vector_db

# Copy environment variables template
echo ""
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file - Please update with your API keys"
else
    echo "✓ .env file already exists"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x scripts/*.py
chmod +x scripts/*.sh

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Add your medical datasets to data/ directories"
echo "3. Run: python scripts/process_data.py"
echo "4. Run: python scripts/run_server.py"
echo ""
echo "For testing: pytest tests/ -v"
echo ""
