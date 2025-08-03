#!/usr/bin/env python3
"""
Test script to verify all dependencies are properly installed
"""

import sys

def test_imports():
    """Test that all required packages can be imported"""
    packages = [
        ("transformers", "Transformers (Hugging Face)"),
        ("torch", "PyTorch"),
        ("symspellpy", "SymSpellPy"),
        ("spacy", "spaCy"),
        ("nltk", "NLTK"),
        ("sentence_transformers", "Sentence Transformers"),
        ("llmlingua", "LLMLingua"),
        ("txtai", "txtai"),
        ("rich", "Rich (Terminal UI)"),
        ("yaml", "PyYAML"),
        ("click", "Click"),
        ("tqdm", "tqdm"),
        ("pandas", "Pandas"),
    ]
    
    print("Testing package imports...")
    print("-" * 50)
    
    failed = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name:30} OK")
        except ImportError as e:
            print(f"❌ {name:30} FAILED - {str(e)}")
            failed.append(name)
    
    print("-" * 50)
    
    if failed:
        print(f"\n⚠️  {len(failed)} packages failed to import:")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\nRun './setup_project.sh' to install missing dependencies")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_token_counter():
    """Test basic tokenization"""
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained('gpt2')
        text = "Hello world!"
        tokens = tokenizer.encode(text)
        print(f"\n✅ Tokenizer test passed: '{text}' = {len(tokens)} tokens")
        return True
    except Exception as e:
        print(f"\n❌ Tokenizer test failed: {str(e)}")
        return False

def test_spacy_model():
    """Test spaCy model is downloaded"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("Test sentence")
        print(f"✅ spaCy model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
        return False

if __name__ == "__main__":
    print("LLM Cost Optimization - Installation Test")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print("=" * 50)
    print()
    
    # Run tests
    imports_ok = test_imports()
    tokenizer_ok = test_token_counter()
    spacy_ok = test_spacy_model()
    
    # Summary
    print("\n" + "=" * 50)
    if imports_ok and tokenizer_ok and spacy_ok:
        print("✅ All tests passed! The environment is ready.")
        print("\nNext steps:")
        print("1. cd token-optimizer")
        print("2. python pipeline.py --help")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please run './setup_project.sh' to fix issues.")
        sys.exit(1)