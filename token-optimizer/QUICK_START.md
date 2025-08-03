# Quick Start Guide

## 1. Initial Setup (one time only)
```bash
./setup.sh
source venv/bin/activate
```

## 2. Test the Pipeline
```bash
# Run the demo
./demo.sh

# Or test with your own text
echo "Your verbose text here" | python pipeline.py
```

## 3. Common Use Cases

### Optimize a prompt file:
```bash
python pipeline.py my_prompt.txt -o optimized.txt
```

### Check token count:
```bash
python pipeline.py my_prompt.txt --count-only
```

### See what optimizations are possible:
```bash
python pipeline.py my_prompt.txt --analyze
```

### Use specific stages only:
```bash
# Just abbreviations and token-aware
python pipeline.py input.txt --stages abbreviations token_aware
```

## 4. Integration Examples

### In a bash script:
```bash
#!/bin/bash
PROMPT=$(cat my_prompt.txt | python /path/to/pipeline.py)
curl -X POST api.openai.com/v1/completions -d "{\"prompt\": \"$PROMPT\"}"
```

### As a pre-processor:
```bash
alias llm-optimize='python /path/to/token-optimizer/pipeline.py'
echo "my long prompt" | llm-optimize | your-llm-command
```

### For different models:
```bash
# For GPT-4
sed -i 's/model: "gpt2"/model: "gpt-4"/' config/pipeline_config.yaml

# For Claude
sed -i 's/model: "gpt2"/model: "claude"/' config/pipeline_config.yaml
```

## Performance Tips

- **Fastest** (rule-based only): Disable ML paraphrasing in config
- **Best compression**: Enable all stages, use aggressive ratios
- **Real-time**: Use only stages 1-3 (no ML)