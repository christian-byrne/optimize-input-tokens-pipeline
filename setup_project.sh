#!/bin/bash

echo "Setting up Token Optimization Project Environment"
echo "================================================"
echo

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing project requirements..."
pip install -r requirements.txt

# Download required models/data
echo "Downloading required language models..."
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt')"

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p data/cache
mkdir -p output
mkdir -p notebooks

# Create .env file template
cat > .env.example << 'EOF'
# Token Optimization Configuration

# Model settings
DEFAULT_TOKENIZER=gpt2
DEFAULT_LLM=t5-small

# API Keys (if needed)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Performance settings
BATCH_SIZE=32
MAX_WORKERS=4
CACHE_ENABLED=true

# Logging
LOG_LEVEL=INFO
EOF

echo
echo "✅ Setup complete!"
echo
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo
echo "To run the token optimizer pipeline:"
echo "  cd token-optimizer"
echo "  python pipeline.py --help"
echo
echo "To deactivate the environment when done:"
echo "  deactivate"