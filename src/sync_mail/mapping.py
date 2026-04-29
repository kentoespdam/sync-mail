# src/sync_mail/mapping.py

import os
from typing import Dict, Any, List
from ruamel.yaml import YAML

from sync_mail.errors import MappingError
from sync_mail.observability import event_bus, EventType

class MappingConfigLoader:
    """
    Handles loading and validating YAML mapping configurations.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.yaml_handler = YAML()
        self.yaml_handler.indent(mapping=2, sequence=4, offset=2)
        self.yaml_handler.width = 4096

    def load_mapping(self) -> Dict[str, Any]:
        """
        Loads and validates the YAML mapping configuration from the specified path.

        Returns:
            Dict[str, Any]: The validated mapping configuration.

        Raises:
            MappingError: If the configuration file is not found, cannot be read,
                          or fails validation.
        """
        if not os.path.exists(self.config_path):
            error_message = f"Mapping configuration file not found at: {self.config_path}"
            event_bus.publish(
                event_bus.Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "config_path": self.config_path}
                )
            )
            raise MappingError(error_message, context={"config_path": self.config_path})

        try:
            with open(self.config_path, 'r') as file:
                mapping_data = self.yaml_handler.load(file)
            
            # Basic validation: Check if it's a dictionary and has expected top-level keys
            if not isinstance(mapping_data, dict):
                raise MappingError("Invalid mapping format: root must be a dictionary.")
            
            # Example validation: Check for 'schema' and 'tables' keys
            # This validation can be expanded significantly based on specific YAML structure rules.
            if "schema" not in mapping_data:
                raise MappingError("Invalid mapping format: 'schema' key is missing.")
            if "tables" not in mapping_data or not isinstance(mapping_data["tables"], list):
                raise MappingError("Invalid mapping format: 'tables' must be a list.")
            
            # Further validation for each table and its columns can be added here.
            # For now, we assume the structure is valid if these keys exist.

            event_bus.publish(
                event_bus.Event(
                    event_type=EventType.JOB_STARTED, # Generic event for now
                    payload={"message": f"Mapping configuration loaded and validated from {self.config_path}"}
                )
            )
            return mapping_data

        except FileNotFoundError: # Already checked, but good practice
            error_message = f"Mapping configuration file not found at: {self.config_path}"
            event_bus.publish(
                event_bus.Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "config_path": self.config_path}
                )
            )
            raise MappingError(error_message, context={"config_path": self.config_path}) from None
        except Exception as e:
            error_message = f"Failed to load or validate mapping configuration from {self.config_path}: {e}"
            event_bus.publish(
                event_bus.Event(
                    event_type=EventType.JOB_ABORTED,
                    payload={"error": error_message, "config_path": self.config_path}
                )
            )
            raise MappingError(error_message, context={"config_path": self.config_path, "exception": str(e)}) from e

# Example usage (would be called from CLI handler):
# if __name__ == "__main__":
#     # Assume a dummy mapping.yaml exists for testing purposes
#     # content of dummy_mapping.yaml:
#     # schema: my_schema
#     # tables:
#     #   - name: users
#     #     columns:
#     #       - name: id
#     #         type: integer
#     #         primary_key: true
#     #         autoincrement: true
#     #       - name: username
#     #         type: string
#     #         nullable: false
#     
#     # Create a dummy file for testing
#     dummy_config_path = "dummy_mapping.yaml"
#     with open(dummy_config_path, "w") as f:
#         f.write("""
# schema: my_schema
# tables:
#   - name: users
#     columns:
#       - name: id
#         type: integer
#         primary_key: true
#         autoincrement: true
#       - name: username
#         type: string
#         nullable: false
# """)
#
#     loader = MappingConfigLoader(dummy_config_path)
#     try:
#         print(f"Loading mapping from {dummy_config_path}...")
#         mapping = loader.load_mapping()
#         print("Mapping loaded successfully:")
#         print(mapping)
#     except MappingError as me:
#         print(f"Error loading mapping: {me}")
#     finally:
#         # Clean up dummy file
#         if os.path.exists(dummy_config_path):
#             os.remove(dummy_config_path)
