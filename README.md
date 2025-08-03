# LLM Cost Optimization Toolkit

A comprehensive collection of tools and strategies for reducing LLM API costs through intelligent token optimization.

## 🎯 Project Goal
Reduce LLM API costs by 50-80% through intelligent preprocessing, compression, and optimization techniques while maintaining output quality.

## 📁 Repository Structure

```
llm-cost-optimization/
├── token-optimizer/          # Main pipeline implementation
│   ├── pipeline.py          # Core orchestrator with verbose mode
│   ├── scripts/             # Individual optimization stages
│   │   ├── 01_spell_check.py
│   │   ├── 02_abbreviations.py
│   │   ├── 03_token_aware.py
│   │   └── 04_ml_paraphrase.py
│   ├── config/              # Configuration files
│   ├── utils/               # Utilities (diff viewer, etc.)
│   └── examples/            # Usage examples
├── docs/                    # Research and documentation
│   ├── ideas-brainstorm.md
│   ├── text-normalization-approaches.md
│   └── implementation-plan.md
├── requirements.txt         # Python dependencies
├── setup_project.sh         # One-click setup script
└── todo.md                 # Project task tracking
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone and setup
cd llm-cost-optimization
./setup_project.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Basic Usage
```bash
# Navigate to token optimizer
cd token-optimizer

# Process text
echo "Please could you help me understand this?" | python pipeline.py
# Output: "help understand this?"

# Process file with verbose mode
python pipeline.py input.txt --verbose

# Analyze optimization potential
python pipeline.py document.txt --analyze
```

### 3. Advanced Features
```bash
# Use specific stages only
python pipeline.py input.txt --stages abbreviations token_aware

# Different tokenizer models
sed -i 's/model: "gpt2"/model: "gpt-4"/' config/pipeline_config.yaml

# Run the demo
./demo.sh
```

## 🛠️ Features

### Token Optimizer Pipeline
- **Modular Architecture**: 4 independent stages that can be mixed and matched
- **Smart Token Counting**: Actual token measurement for your target LLM
- **ML Compression**: Uses small models (T5-small) for intelligent paraphrasing
- **Beautiful Verbose Mode**: Visual diffs, statistics, and progress tracking
- **Configurable**: YAML configuration for easy customization

### Optimization Techniques
1. **Spell Correction**: Fix typos that waste tokens
2. **Smart Abbreviations**: Context-aware replacements
3. **Token-Aware Optimization**: Only changes that actually save tokens
4. **ML Paraphrasing**: Intelligent compression using small language models

## 📊 Performance

Typical results on real-world prompts:
- **Token Reduction**: 30-60%
- **Processing Time**: <500ms (without ML), <2s (with ML)
- **Quality Preservation**: 95%+ semantic similarity

## 🔧 Configuration

Edit `token-optimizer/config/pipeline_config.yaml`:

```yaml
tokenizer:
  model: "gpt2"  # or "gpt-4", "claude", etc.

pipeline:
  spell_check:
    enabled: true
  abbreviations:
    enabled: true
  token_aware:
    enabled: true
  ml_paraphrase:
    enabled: true
    model: "t5-small"
    max_length_ratio: 0.8
```

## 📚 Documentation

- [Ideas & Brainstorming](ideas-brainstorm.md) - Comprehensive strategies list
- [Research Topics](topics-and-ideas-to-research-and-consider.md) - Academic and industry research
- [Text Normalization Approaches](text-normalization-approaches.md) - All possible methods
- [Implementation Plan](implementation-plan.md) - Technical implementation guide
- [Todo List](todo.md) - Project tasks and progress

## 🤝 Contributing

This project is designed for parallel development. Check [todo.md](todo.md) for available tasks.

### Development Workflow
1. Pick a task from todo.md
2. Create a new branch
3. Implement and test
4. Update documentation
5. Submit PR

## 🧪 Testing

### Quick Test
```bash
# Run basic tests
./run_tests.sh
```

### Full Test Suite
```bash
# Unit tests with coverage
make ci-test

# All CI checks (format, lint, type, test)
make ci

# Individual checks
make ci-format    # Format code
make ci-lint      # Run linters
make ci-typecheck # Type checking
```

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures and helpers
├── unit/                    # Fast, isolated unit tests
│   ├── test_spell_check.py
│   ├── test_abbreviations.py
│   ├── test_token_aware.py
│   └── test_pipeline.py
└── integration/             # End-to-end integration tests
    └── test_full_pipeline.py
```

### Writing Tests
```python
# Use provided fixtures
def test_example(sample_text, abbreviations_dict, test_helpers):
    result = process(sample_text)
    assert test_helpers.calculate_reduction(sample_text, result) > 30
```

## 📈 Roadmap

- [x] Core pipeline implementation
- [x] Verbose mode with visual diffs
- [ ] Web interface
- [ ] Real-time optimization API
- [ ] Custom model training
- [ ] Integration plugins (VSCode, CLI tools)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Microsoft Research for LLMLingua
- Hugging Face for transformers library
- Rich library for beautiful terminal UI