"""
Helper functions for importing token optimizer modules in tests
"""

import importlib.util
import sys
from pathlib import Path


def import_script_module(script_name):
    """Import a script module from token-optimizer/scripts"""
    scripts_path = Path(__file__).parent.parent / "token-optimizer/scripts"
    script_file = scripts_path / script_name

    if not script_file.exists():
        raise ImportError(f"Script not found: {script_file}")

    # Create module name from filename
    module_name = script_file.stem.replace("-", "_")

    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, script_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


# Pre-import common modules
def get_spell_checker():
    """Get SpellChecker class"""
    module = import_script_module("01_spell_check.py")
    return module.SpellChecker


def get_abbreviation_replacer():
    """Get AbbreviationReplacer class"""
    module = import_script_module("02_abbreviations.py")
    return module.AbbreviationReplacer


def get_token_aware_optimizer():
    """Get TokenAwareOptimizer class"""
    module = import_script_module("03_token_aware.py")
    return module.TokenAwareOptimizer


def get_ml_paraphraser():
    """Get MLParaphraser class"""
    module = import_script_module("04_ml_paraphrase.py")
    return module.MLParaphraser
