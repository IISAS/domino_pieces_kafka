from __future__ import annotations

from enum import Enum
from typing import Set


class PieceEnum(str, Enum):

    @classmethod
    def from_string(cls, value: str) -> "PieceEnum":
        """
        Parse enum member from string (case-insensitive).
        Raises ValueError if invalid.
        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value!r} is not a valid {cls.__name__}. "
            f"Allowed values: {sorted(cls.values())}"
        )

    @classmethod
    def title(cls) -> str:
        raise NotImplementedError(
            f"{cls.__name__} must implement title()"
        )

    @classmethod
    def values(cls) -> Set[str]:
        return {member.value for member in cls}

    def __str__(self) -> str:
        return self.value


class SecurityProtocol(PieceEnum):
    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"

    @classmethod
    def title(cls) -> str:
        return "security.protocol"


class CleanupPolicy(PieceEnum):
    compact = "compact"
    delete = "delete"

    @classmethod
    def title(cls) -> str:
        return "cleanup.policy"


class Acks(PieceEnum):
    all = "all"
    file_and_forget = "fire_and_forget"
    wait_for_leader = "wait_for_leader"

    @classmethod
    def title(cls) -> str:
        return "acks"
