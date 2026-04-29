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

def resolve_connection_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolves database connection configuration from YAML or interactive input.
    Follows a 3-step check:
    1. Check file existence.
    2. Check file content (not empty).
    3. Check block completeness (source & target).
    
    Falls back to interactive input if any check fails.
    """
    path = config_path or DEFAULT_CONNECTION_FILE
    
    # 1. Try to load from YAML
    yaml_config, status = _load_from_yaml(path)
    
    if status == "VALID":
        # Log success (without credentials)
        logger.info(f"Connection configuration loaded successfully from '{path}'")
        _check_gitignore(path)
        return yaml_config
    
    # 2. Inform user about the situation
    if status == "MISSING_FILE":
        print(f"\n[INFO] Connection file '{path}' not found.")
    elif status == "EMPTY_FILE":
        print(f"\n[INFO] Connection file '{path}' is empty.")
    elif status == "INVALID_FORMAT":
        print(f"\n[WARNING] Connection file '{path}' has an invalid format. Root must be a dictionary.")
    elif "PARSE_ERROR" in status:
        print(f"\n[ERROR] Failed to parse '{path}': {status.split(':', 1)[1]}")
    else:
        print(f"\n[INFO] Connection file '{path}' is incomplete ({status}).")
    
    print("Starting interactive connection setup...\供")

    # 3. Fallback to interactive input
    # Silence logger stdout to avoid overlapping with prompts
    with _silence_stdout():
        final_config = _prompt_for_config(yaml_config, status)
        
    # Re-check gitignore after manual input if it might be saved (though we don't save it yet as per requirements)
    _check_gitignore(path)
    
    return final_config

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

def _prompt_for_config(initial_data: Dict[str, Any], status: str) -> Dict[str, Any]:
    """Prompts for missing fields in source and/or target blocks."""
    config = {
        "source": initial_data.get("source", {}),
        "target": initial_data.get("target", {})
    }
    
    if not isinstance(config["source"], dict): config["source"] = {}
    if not isinstance(config["target"], dict): config["target"] = {}

    print("-" * 40)
    print("Database Connection Setup")
    print("-" * 40)

    # Determine which blocks need prompting
    prompt_source = status in ["MISSING_FILE", "EMPTY_FILE", "INVALID_FORMAT", "BOTH_INCOMPLETE", "SOURCE_INCOMPLETE"] or "PARSE_ERROR" in status
    prompt_target = status in ["MISSING_FILE", "EMPTY_FILE", "INVALID_FORMAT", "BOTH_INCOMPLETE", "TARGET_INCOMPLETE"] or "PARSE_ERROR" in status

    if prompt_source:
        print("\n[SOURCE DATABASE]")
        config["source"] = _prompt_block(config["source"])
    
    if prompt_target:
        print("\n[TARGET DATABASE]")
        config["target"] = _prompt_block(config["target"])

    print("\nConnection configuration complete.\n")
    return config

def _prompt_block(existing: Dict[str, Any]) -> Dict[str, Any]:
    """Prompts for host, port, user, password, database."""
    block = existing.copy()
    
    block["host"] = _ask("Host", default=block.get("host", "localhost"))
    
    while True:
        port_str = _ask("Port", default=str(block.get("port", 3306)))
        try:
            block["port"] = int(port_str)
            break
        except ValueError:
            print("Invalid port. Please enter a number.")

    block["user"] = _ask("User", default=block.get("user"))
    while not block["user"]:
        print("User cannot be empty.")
        block["user"] = _ask("User")

    # Password input (hidden)
    pwd_input = getpass.getpass(f"Password (default: {'*' * 8 if block.get('password') else 'None'}): ").strip()
    if not pwd_input and "password" in block and block["password"]:
        # Keep existing password if input is empty
        pass
    else:
        block["password"] = pwd_input

    block["database"] = _ask("Database", default=block.get("database"))
    while not block["database"]:
        print("Database name cannot be empty.")
        block["database"] = _ask("Database")

    return block

def _ask(label: str, default: Optional[str] = None) -> str:
    prompt = f"{label}"
    if default:
        prompt += f" (default: {default})"
    prompt += ": "
    
    val = input(prompt).strip()
    return val if val else (default or "")

@contextmanager
def _silence_stdout():
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
        print(f"\n[SECURITY WARNING] .gitignore not found. Please ensure '{path}' is not committed.")
        return

    try:
        with open(".gitignore", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        filename = os.path.basename(path)
        is_ignored = any(filename in line and not line.strip().startswith("#") for line in lines)
        
        if not is_ignored:
            print(f"\n[SECURITY WARNING] '{filename}' is NOT detected in .gitignore.")
            print(f"It is highly recommended to add '{filename}' to .gitignore to avoid leaking credentials.")
    except Exception:
        # Don't crash if we can't read .gitignore
        pass
