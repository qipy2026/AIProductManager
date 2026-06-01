"""Skill Registry — 加载与校验 Manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

MANIFESTS_DIR = Path(__file__).resolve().parents[1] / "manifests"
SCHEMA_PATH = MANIFESTS_DIR / "schema.json"


class SkillRegistry:
    def __init__(self, manifests_dir: Path | None = None) -> None:
        self.manifests_dir = manifests_dir or MANIFESTS_DIR
        self._cache: dict[str, dict[str, Any]] = {}

    def list_skills(self) -> list[str]:
        return sorted(p.stem for p in self.manifests_dir.glob("*.yaml"))

    def load(self, skill_id: str, version: str | None = None) -> dict[str, Any]:
        key = f"{skill_id}@{version}" if version else skill_id
        if key in self._cache:
            return self._cache[key]

        path = self.manifests_dir / f"{skill_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Skill manifest not found: {skill_id}")

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if version and data.get("version") != version:
            raise ValueError(f"Skill {skill_id} version mismatch: want {version}, got {data.get('version')}")

        self._cache[key] = data
        return data

    def load_all(self) -> dict[str, dict[str, Any]]:
        return {sid: self.load(sid) for sid in self.list_skills()}

    def validate_schema(self, data: dict[str, Any]) -> bool:
        required = ["id", "version", "name", "agent", "boundary", "tools", "memory_deps"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        boundary = data["boundary"]
        if "does" not in boundary or "does_not" not in boundary:
            raise ValueError("boundary must have does and does_not")
        return True
