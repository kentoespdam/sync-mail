import os
import sys
import getpass
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple, List
from ruamel.yaml import YAML
from sync_mail.errors import ConfigError
from sync_mail.observability import logger

DEFAULT_CONNECTION_FILE = "connection.yaml"

def resolve_connection_config(config_path: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
    """
    Resolves database connection configuration from YAML.
    Returns (config_dict, status_string).
    
    Status strings:
    - VALID: File exists and has all required fields.
    - MISSING_FILE: connection.yaml not found.
    - EMPTY_FILE: File is zero bytes.
    - INVALID_FORMAT: YAML root is not a dictionary.
    - PARSE_ERROR: YAML syntax error.
    - SOURCE_INCOMPLETE: Missing fields in 'source' block.
    - TARGET_INCOMPLETE: Missing fields in 'target' block.
    - BOTH_INCOMPLETE: Missing fields in both blocks.
    """
    path = config_path or DEFAULT_CONNECTION_FILE
    
    # Try to load from YAML
    yaml_config, status = _load_from_yaml(path)
    
    if os.path.exists(path):
        _check_gitignore(path)
        
    if status == "VALID":
        # Log success (without credentials)
        logger.info(f"Connection configuration loaded successfully from '{path}'")
    
    return yaml_config, status

def _load_from_yaml(path: str) -> Tuple[Dict[str, Any], str]:
    """Loads YAML and returns (data, status_string)"""
    if not os.path.exists(path):
        return {}, "MISSING_FILE"
    
    try:
        if os.path.getsize(path) == 0:
            return {}, "EMPTY_FILE"
    except OSError:
        return {}, "MISSING_FILE"
        
    yaml = YAML(typ="safe")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
    except Exception as e:
        return {}, f"PARSE_ERROR: {str(e)}"

    if not data or not isinstance(data, dict):
        return {}, "INVALID_FORMAT"

    source = data.get("source", {})
    target = data.get("target", {})
    
    if not isinstance(source, dict): source = {}
    if not isinstance(target, dict): target = {}
    
    required_fields = ["host", "port", "user", "password", "database"]
    
    source_missing = [f for f in required_fields if f not in source or source[f] is None]
    target_missing = [f for f in required_fields if f not in target or target[f] is None]
    
    if not source_missing and not target_missing:
        return data, "VALID"
        
    if source_missing and target_missing:
        return data, "BOTH_INCOMPLETE"
    elif source_missing:
        return data, "SOURCE_INCOMPLETE"
    else:
        return data, "TARGET_INCOMPLETE"

@contextmanager
def silence_stdout():
    """Temporarily disables stdout logging handler."""
    root_logger = logging.getLogger()
    stdout_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout]
    
    # Save original levels
    original_levels = {h: h.level for h in stdout_handlers}
    
    try:
        for h in stdout_handlers:
            h.setLevel(logging.CRITICAL + 1) # Effectively silence
        yield
    finally:
        for h, level in original_levels.items():
            h.setLevel(level)

def _check_gitignore(path: str):
    """Checks if the connection file is in .gitignore and warns if not."""
    if not os.path.exists(".gitignore"):
        logger.warning(f".gitignore not found. Please ensure '{path}' is not committed.")
        return

    try:
        with open(".gitignore", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        filename = os.path.basename(path)
        is_ignored = any(filename in line and not line.strip().startswith("#") for line in lines)
        
        if not is_ignored:
            logger.warning(f"'{filename}' is NOT detected in .gitignore. Recommended to add it to avoid leaking credentials.")
    except Exception:
        # Don't crash if we can't read .gitignore
        pass
