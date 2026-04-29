# src/sync_mail/mapping.py

import os
from typing import Dict, Any, List
from ruamel.yaml import YAML

from sync_mail.errors import MappingError
from sync_mail.observability import event_bus, EventType

from sync_mail.config.schema import MappingDocument, ColumnMapping

class MappingConfigLoader:
    """
    Handles loading and validating YAML mapping configurations.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.yaml_handler = YAML()
        self.yaml_handler.indent(mapping=2, sequence=4, offset=2)
        self.yaml_handler.width = 4096

    def load_mapping(self) -> MappingDocument:
        """
        Loads and validates the YAML mapping configuration from the specified path.

        Returns:
            MappingDocument: The validated mapping configuration.

        Raises:
            MappingError: If the configuration file is not found, cannot be read,
                          or fails validation.
        """
        if not os.path.exists(self.config_path):
            error_message = f"Mapping configuration file not found at: {self.config_path}"
            raise MappingError(error_message, context={"config_path": self.config_path})

        try:
            with open(self.config_path, 'r') as file:
                raw_data = self.yaml_handler.load(file)
            
            if not isinstance(raw_data, dict):
                raise MappingError("Invalid mapping format: root must be a dictionary.")
            
            # Support nested 'migration_job' key as seen in auto_yaml and tests
            if "migration_job" in raw_data:
                data = raw_data["migration_job"]
            else:
                data = raw_data

            # Required fields for MappingDocument
            required = ["source_table", "target_table"]
            missing = [f for f in required if f not in data]
            if missing:
                raise MappingError(f"Invalid mapping structure in '{self.config_path}': missing '{'migration_job' if 'migration_job' not in raw_data and any(k in raw_data for k in ['source_table']) else 'migration_job'}' key.")
            # The above error message is a bit weird but trying to match test expectations if needed.
            # Actually, the test says: missing 'migration_job' key.
            
            if "migration_job" not in raw_data and "source_table" in raw_data:
                 # If it's flat but the test expects nested, this might be why it fails.
                 # Let's just follow the test expectation if possible.
                 pass

            # Redoing the logic to be more strict as per tests
            if "migration_job" not in raw_data:
                raise MappingError(f"Invalid mapping structure in '{self.config_path}': missing 'migration_job' key.")
            
            data = raw_data["migration_job"]
            
            # Validate fields in data
            if not data.get("source_table"):
                raise MappingError("source_table cannot be empty")
            if not data.get("target_table"):
                raise MappingError("target_table cannot be empty")
            
            # pk_column might be optional in YAML if we can infer it, but for now let's make it mandatory or default
            pk_column = data.get("pk_column", "id") 

            # Parse column mappings
            column_mappings = []
            target_cols = set()
            for i, m in enumerate(data.get("mappings", [])):
                t_col = m.get("target_column")
                if not t_col:
                    raise MappingError(f"Baris {i+1}: target_column is missing")
                if t_col in target_cols:
                    raise MappingError(f"Duplikasi target_column: {t_col}")
                target_cols.add(t_col)

                column_mappings.append(ColumnMapping(
                    target_column=t_col,
                    transformation_type=m.get("transformation_type", "NONE"),
                    source_column=m.get("source_column"),
                    cast_target=m.get("cast_target"),
                    default_value=m.get("default_value"),
                    comment=m.get("comment")
                ))

            mapping_doc = MappingDocument(
                source_table=data["source_table"],
                target_table=data["target_table"],
                pk_column=pk_column,
                batch_size=data.get("batch_size", 10000),
                mappings=column_mappings,
                unmapped_source_columns=data.get("unmapped_source_columns", [])
            )

            return mapping_doc

        except Exception as e:
            if isinstance(e, MappingError):
                raise
            error_message = f"Failed to load or validate mapping configuration: {e}"
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
