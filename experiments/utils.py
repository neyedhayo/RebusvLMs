import os
import yaml
from typing import Any, Dict


def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def expand_env_vars_recursive(data: Any) -> Any:
    """
    Recursively expand environment variables in strings within nested data structures.
    Works with dicts, lists, and strings.
    """
    if isinstance(data, dict):
        return {key: expand_env_vars_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [expand_env_vars_recursive(item) for item in data]
    elif isinstance(data, str):
        return os.path.expandvars(data)
    else:
        return data


def load_config_files(base_config_path: str, model_config_path: str) -> Dict[str, Any]:
    """
    Load and merge base and model-specific config files with environment variable expansion.
    """
    # Load base config
    with open(base_config_path, 'r', encoding='utf-8') as f:
        base_config = yaml.safe_load(f)
    
    # Load model-specific config
    with open(model_config_path, 'r', encoding='utf-8') as f:
        model_config = yaml.safe_load(f)
    
    # Merge configs (model config overrides base config)
    merged_config = {**base_config, **model_config}
    
    # Expand environment variables recursively
    expanded_config = expand_env_vars_recursive(merged_config)
    
    return expanded_config