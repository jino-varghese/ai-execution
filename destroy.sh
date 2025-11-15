#!/bin/bash

# AI Travel Itinerary Generator - Cleanup Script
# This script destroys all AWS resources

set -e

echo "================================"
echo "Resource Cleanup"
echo "================================"
echo ""
echo "⚠️  WARNING: This will destroy all deployed resources!"
echo ""

read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Navigate to terraform directory
cd "$(dirname "$0")/terraform"

echo ""
echo "Destroying resources..."
terraform destroy

echo ""
echo "================================"
echo "All resources have been destroyed"
echo "================================"
