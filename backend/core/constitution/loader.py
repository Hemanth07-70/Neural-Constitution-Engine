"""Loader for parsing JSON and YAML into Constitution objects."""

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from .constitution import Constitution
from .exceptions import ConstitutionLoaderError, ConstitutionParseError, ConstitutionValidationError
from .metadata import Metadata, Resolution
from .rule import Principle, Rule, RuleAction


class ConstitutionLoader:
    """Loads Constitution YAML and JSON files into immutable domain objects."""

    def load_file(self, path: Path | str) -> Constitution:
        """Load a constitution from a JSON or YAML file."""
        filepath = Path(path)
        if not filepath.exists():
            raise ConstitutionLoaderError(f"File not found: {filepath}")

        text = filepath.read_text(encoding="utf-8")
        
        try:
            if filepath.suffix in (".yaml", ".yml"):
                if yaml is None:
                    raise ConstitutionLoaderError("PyYAML is required to load YAML constitutions.")
                data = yaml.safe_load(text)
            elif filepath.suffix == ".json":
                data = json.loads(text)
            else:
                raise ConstitutionLoaderError(f"Unsupported file extension: {filepath.suffix}")
        except Exception as e:
            if isinstance(e, ConstitutionLoaderError):
                raise
            raise ConstitutionParseError(f"Failed to parse {filepath}: {e}") from e

        if not isinstance(data, dict):
            raise ConstitutionValidationError(f"Expected a mapping at root, got {type(data).__name__}")

        return self.load_dict(data)

    def load_dict(self, data: dict[str, Any]) -> Constitution:
        """Construct a Constitution from a raw dictionary."""
        api_version = data.get("apiVersion")
        kind = data.get("kind")
        
        if not api_version or not kind:
            raise ConstitutionValidationError("Missing required top-level fields 'apiVersion' or 'kind'")

        metadata_dict = data.get("metadata")
        if not isinstance(metadata_dict, dict):
            raise ConstitutionValidationError("Missing or invalid 'metadata' block")

        metadata = Metadata(
            id=metadata_dict.get("id"),
            version=metadata_dict.get("version"),
            scope=metadata_dict.get("scope"),
            title=metadata_dict.get("title"),
            description=metadata_dict.get("description"),
            author=metadata_dict.get("author"),
            created_at=metadata_dict.get("created_at"),
            updated_at=metadata_dict.get("updated_at"),
            status=metadata_dict.get("status"),
            extends=metadata_dict.get("extends"),
        )
        if not metadata.id or not metadata.version or not metadata.scope:
            raise ConstitutionValidationError("Metadata is missing required fields (id, version, scope)")

        resolution = None
        resolution_dict = data.get("resolution")
        if resolution_dict is not None:
            if not isinstance(resolution_dict, dict):
                raise ConstitutionValidationError("Invalid 'resolution' block")
            resolution = Resolution(
                strategy=resolution_dict.get("strategy"),
                default_verdict=resolution_dict.get("default_verdict"),
            )
            if not resolution.strategy or not resolution.default_verdict:
                raise ConstitutionValidationError("Resolution is missing required fields")

        principles_list = data.get("principles", [])
        if not isinstance(principles_list, list):
            raise ConstitutionValidationError("Invalid 'principles' block")
        
        principles = []
        for p in principles_list:
            if not isinstance(p, dict):
                raise ConstitutionValidationError("Principle must be an object")
            if not p.get("id") or not p.get("statement") or not p.get("category"):
                raise ConstitutionValidationError("Principle missing required fields (id, statement, category)")
            principles.append(Principle(
                id=p["id"],
                statement=p["statement"],
                category=p["category"],
            ))

        rules_list = data.get("rules", [])
        if not isinstance(rules_list, list):
            raise ConstitutionValidationError("Invalid 'rules' block")
        
        rules = []
        for r in rules_list:
            if not isinstance(r, dict):
                raise ConstitutionValidationError("Rule must be an object")
            if not r.get("id") or "condition" not in r or "action" not in r:
                raise ConstitutionValidationError("Rule missing required fields (id, condition, action)")
            
            action_dict = r["action"]
            if not isinstance(action_dict, dict) or not action_dict.get("type"):
                raise ConstitutionValidationError("Rule action is missing or invalid")
            
            action = RuleAction(
                type=action_dict["type"],
                message=action_dict.get("message"),
                approver_role=action_dict.get("approver_role"),
                transform=action_dict.get("transform"),
            )
            
            cond = r["condition"]
            if not isinstance(cond, dict):
                raise ConstitutionValidationError("Rule condition must be an object")
            
            rule_principle = r.get("principle")
            if isinstance(rule_principle, list):
                rule_principle = tuple(rule_principle)
                
            rules.append(Rule(
                id=r["id"],
                condition=MappingProxyType(cond),
                action=action,
                title=r.get("title"),
                description=r.get("description"),
                principle=rule_principle,
                category=r.get("category"),
                tags=tuple(r.get("tags", [])),
                severity=r.get("severity"),
                enabled=r.get("enabled", True),
                priority=r.get("priority", 0),
                references=tuple(r.get("references", [])),
            ))

        return Constitution(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            resolution=resolution,
            principles=tuple(principles),
            rules=tuple(rules),
        )
