"""Profile Memory — VIP / 套餐 / 偏好."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserProfile:
    user_id: str
    tier: str = "standard"
    plan: str = "专业版"
    preferences: dict | None = None

    def to_context(self) -> dict:
        return {
            "tier": self.tier,
            "plan": self.plan,
            "preferences": self.preferences or {},
        }


class ProfileMemoryStore:
    def __init__(self) -> None:
        self._profiles: dict[str, UserProfile] = {
            "user_vip": UserProfile(user_id="user_vip", tier="VIP", plan="企业版"),
            "C-1001": UserProfile(user_id="C-1001", tier="VIP", plan="企业版"),
        }

    def get(self, user_id: str) -> UserProfile | None:
        if not user_id:
            return None
        if user_id in self._profiles:
            return self._profiles[user_id]
        return UserProfile(user_id=user_id)

    def set(self, profile: UserProfile) -> None:
        self._profiles[profile.user_id] = profile

    def clear(self) -> None:
        self._profiles = {
            "user_vip": UserProfile(user_id="user_vip", tier="VIP", plan="企业版"),
            "C-1001": UserProfile(user_id="C-1001", tier="VIP", plan="企业版"),
        }
