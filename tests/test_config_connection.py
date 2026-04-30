import unittest
import os
import tempfile
from ruamel.yaml import YAML
from sync_mail.config.connection import resolve_connection_config

class TestConfigConnection(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.test_dir.name, "connection.yaml")
        self.yaml = YAML(typ="safe")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_missing_file(self):
        config, status = resolve_connection_config(self.config_path)
        self.assertEqual(config, {})
        self.assertEqual(status, "MISSING_FILE")

    def test_empty_file(self):
        with open(self.config_path, "w") as f:
            f.write("")
        config, status = resolve_connection_config(self.config_path)
        self.assertEqual(config, {})
        self.assertEqual(status, "EMPTY_FILE")

    def test_valid_file(self):
        data = {
            "source": {
                "host": "s_host", "port": 3306, "user": "s_user", 
                "password": "s_pass", "database": "s_db"
            },
            "target": {
                "host": "t_host", "port": 3307, "user": "t_user", 
                "password": "t_pass", "database": "t_db"
            }
        }
        with open(self.config_path, "w") as f:
            self.yaml.dump(data, f)
        
        config, status = resolve_connection_config(self.config_path)
        self.assertEqual(config["source"]["host"], "s_host")
        self.assertEqual(config["target"]["port"], 3307)
        self.assertEqual(status, "VALID")

    def test_incomplete_source(self):
        data = {
            "source": {"host": "s_host"}, # missing others
            "target": {
                "host": "t_host", "port": 3307, "user": "t_user", 
                "password": "t_pass", "database": "t_db"
            }
        }
        with open(self.config_path, "w") as f:
            self.yaml.dump(data, f)
        
        config, status = resolve_connection_config(self.config_path)
        self.assertEqual(status, "SOURCE_INCOMPLETE")
        self.assertEqual(config["source"]["host"], "s_host")

    def test_invalid_format(self):
        with open(self.config_path, "w") as f:
            f.write("- not a dict")
        
        config, status = resolve_connection_config(self.config_path)
        self.assertEqual(status, "INVALID_FORMAT")

if __name__ == "__main__":
    unittest.main()
