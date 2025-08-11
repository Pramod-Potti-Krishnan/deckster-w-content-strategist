#!/bin/bash
# Script to run tests with virtual environment

# Activate virtual environment
source venv/bin/activate

# Run the test
python test/test_director_e2e.py "$@"