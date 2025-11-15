#!/usr/bin/env python
"""
Script to run the Medical Diagnosis API server
"""

import os
import sys
import uvicorn
import yaml
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))


def main():
    """Run the API server"""

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get API configuration
    host = os.getenv('API_HOST', config['api']['host'])
    port = int(os.getenv('API_PORT', config['api']['port']))
    debug = os.getenv('DEBUG', config['api']['debug'])

    print("=" * 60)
    print("AI-Powered Medical Diagnosis System")
    print("=" * 60)
    print(f"Starting server on {host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Debug mode: {debug}")
    print("=" * 60)
    print("\n⚠️  IMPORTANT DISCLAIMER:")
    print("This system is for RESEARCH and EDUCATIONAL purposes only.")
    print("All AI-generated recommendations must be reviewed by")
    print("licensed healthcare professionals.")
    print("=" * 60)

    # Run server
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
