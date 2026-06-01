"""Skill Registry 测试."""

import pytest

from skills.runtime.registry import SkillRegistry


def test_ut_s_001_load_all_manifests():
    reg = SkillRegistry()
    skills = reg.list_skills()
    assert len(skills) == 12
    for sid in skills:
        data = reg.load(sid)
        assert reg.validate_schema(data) is True


def test_ut_s_002_version_pin():
    reg = SkillRegistry()
    data = reg.load("intent-classify", version="1.0.0")
    assert data["id"] == "intent-classify"


def test_ut_s_002_version_mismatch():
    reg = SkillRegistry()
    with pytest.raises(ValueError):
        reg.load("intent-classify", version="9.9.9")
