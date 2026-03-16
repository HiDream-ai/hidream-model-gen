#!/bin/bash
# Run Vivago AI Skill Test Suite
# Usage: ./run_tests.sh [test_name]

set -e

echo "=================================="
echo "Vivago AI Skill Test Runner"
echo "=================================="

# Change to script directory
cd "$(dirname "$0")/.."

# Check Python
python3 --version || { echo "Python 3 not found"; exit 1; }

# Check dependencies
echo "Checking dependencies..."
python3 -c "import requests, boto3, cv2, numpy" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install -q requests boto3 opencv-python numpy || {
        echo "Failed to install dependencies"
        exit 1
    }
}

# Check environment
if [ -z "$HIDREAM_TOKEN" ]; then
    echo "Warning: HIDREAM_TOKEN not set"
fi

# Run tests
if [ -z "$1" ]; then
    echo "Running all enabled tests..."
    python3 tests/test_suite.py
else
    echo "Running test: $1"
    python3 tests/test_suite.py --test "$1"
fi

echo ""
echo "Test completed. View reports in test_reports/"
