"""Unit tests for the Constitution Loader."""

import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from backend.core.constitution.constitution import Constitution
from backend.core.constitution.exceptions import (
    ConstitutionLoaderError,
    ConstitutionParseError,
    ConstitutionValidationError,
)
from backend.core.constitution.loader import ConstitutionLoader


class TestConstitutionLoader(unittest.TestCase):
    def setUp(self):
        self.loader = ConstitutionLoader()
        self.valid_dict = {
            "apiVersion": "nce/v1",
            "kind": "Constitution",
            "metadata": {
                "id": "org.test.agent",
                "version": "1.0.0",
                "scope": "project",
                "title": "Test Constitution",
            },
            "resolution": {
                "strategy": "most-restrictive-wins",
                "default_verdict": "block",
            },
            "principles": [
                {
                    "id": "P-TEST",
                    "statement": "A test principle.",
                    "category": "safety",
                }
            ],
            "rules": [
                {
                    "id": "R-TEST",
                    "condition": {"field": "action.type", "op": "equals", "value": "test"},
                    "action": {"type": "block", "message": "Test blocked."},
                    "principle": "P-TEST",
                },
                {
                    "id": "R-TEST-2",
                    "condition": {"field": "action.type", "op": "equals", "value": "allow"},
                    "action": {"type": "allow"},
                },
            ],
        }

    def test_load_valid_dict(self):
        constitution = self.loader.load_dict(self.valid_dict)
        self.assertIsInstance(constitution, Constitution)
        self.assertEqual(constitution.api_version, "nce/v1")
        self.assertEqual(constitution.metadata.id, "org.test.agent")
        
        # Test resolution
        self.assertIsNotNone(constitution.resolution)
        self.assertEqual(constitution.resolution.strategy, "most-restrictive-wins")
        
        # Test principles
        self.assertEqual(len(constitution.principles), 1)
        self.assertEqual(constitution.principles[0].id, "P-TEST")
        
        # Test rules and order preservation
        self.assertEqual(len(constitution.rules), 2)
        self.assertEqual(constitution.rules[0].id, "R-TEST")
        self.assertEqual(constitution.rules[1].id, "R-TEST-2")
        self.assertEqual(constitution.rules[0].action.type, "block")
        self.assertIsInstance(constitution.rules[0].condition, MappingProxyType)

    def test_immutability(self):
        constitution = self.loader.load_dict(self.valid_dict)
        with self.assertRaises(FrozenInstanceError):
            constitution.api_version = "nce/v2"  # type: ignore

        with self.assertRaises(FrozenInstanceError):
            constitution.rules[0].id = "R-MUTATED"  # type: ignore
            
        with self.assertRaises(TypeError):
            constitution.rules[0].condition["new_key"] = "value"

    def test_missing_required_fields(self):
        invalid_dict = {"apiVersion": "nce/v1"}
        with self.assertRaises(ConstitutionValidationError):
            self.loader.load_dict(invalid_dict)

        invalid_metadata = self.valid_dict.copy()
        invalid_metadata["metadata"] = {"id": "only-id"}
        with self.assertRaises(ConstitutionValidationError):
            self.loader.load_dict(invalid_metadata)

    def test_load_json_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(self.valid_dict, f)
            filepath = f.name
        
        try:
            constitution = self.loader.load_file(filepath)
            self.assertEqual(constitution.metadata.id, "org.test.agent")
        finally:
            Path(filepath).unlink()

    @unittest.skipIf(yaml is None, "PyYAML not installed")
    def test_load_yaml_file(self):
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            yaml.dump(self.valid_dict, f)
            filepath = f.name
            
        try:
            constitution = self.loader.load_file(filepath)
            self.assertEqual(constitution.metadata.id, "org.test.agent")
        finally:
            Path(filepath).unlink()

    def test_parse_error(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("{ invalid json")
            filepath = f.name
            
        try:
            with self.assertRaises(ConstitutionParseError):
                self.loader.load_file(filepath)
        finally:
            Path(filepath).unlink()

    def test_unsupported_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("text")
            filepath = f.name
            
        try:
            with self.assertRaises(ConstitutionLoaderError) as cm:
                self.loader.load_file(filepath)
            self.assertIn("Unsupported file extension", str(cm.exception))
        finally:
            Path(filepath).unlink()


if __name__ == "__main__":
    unittest.main()
