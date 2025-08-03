#!/bin/bash

echo "Setting up Token Optimizer environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Download spaCy model (small)
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt')"

# Create necessary directories
mkdir -p data/cache
mkdir -p logs
mkdir -p output

echo "Setup complete! Activate the environment with: source venv/bin/activate"