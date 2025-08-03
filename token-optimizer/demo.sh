#!/bin/bash

echo "Token Optimizer Pipeline Demo"
echo "============================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up environment first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

echo "Original text:"
echo "--------------"
cat test_example.txt
echo
echo

echo "Running pipeline..."
echo "==================="
python pipeline.py test_example.txt -o optimized_example.txt

echo
echo "Optimized text:"
echo "---------------"
cat optimized_example.txt
echo
echo

echo "Detailed stage-by-stage analysis:"
echo "================================="

echo
echo "1. After spell check only:"
python pipeline.py test_example.txt --stages spell_check | head -50

echo
echo "2. After spell check + abbreviations:"
python pipeline.py test_example.txt --stages spell_check abbreviations | head -50

echo
echo "3. After spell check + abbreviations + token-aware:"
python pipeline.py test_example.txt --stages spell_check abbreviations token_aware | head -50

echo
echo "Analyzing optimization potential:"
echo "================================"
python pipeline.py test_example.txt --analyze