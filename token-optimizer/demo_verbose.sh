#!/bin/bash

echo "Token Optimizer Pipeline - Verbose Demo"
echo "======================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up environment first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Create a sample text with various optimization opportunities
cat > verbose_demo.txt << 'EOF'
Please could you help me understand the repository configuration and development environment setup?

I would like to know about the following:
- Repository structure and organization
- Environment variables and configurations  
- Authentication and authorization requirements
- Database connection parameters and specifications

It is important to note that the application has multiple environments including development, staging, and production. Can you provide detailed information about the configurations for each environment?

Additionally, I need to understand the dependency management process. The documentation mentions that there are specific requirements for initialization and setup.

Thank you very much for your assistance with this request!
EOF

echo "🎯 Running pipeline with verbose mode..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

python pipeline.py verbose_demo.txt --verbose

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Running analysis mode with verbose output..."
echo

python pipeline.py verbose_demo.txt --analyze --verbose

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎬 Running specific stages with verbose mode..."
echo

echo "Stage 1 & 2 only (Spell check + Abbreviations):"
python pipeline.py verbose_demo.txt --stages spell_check abbreviations --verbose

# Clean up
rm -f verbose_demo.txt optimized_example.txt