from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Transition:
    """
    Represents a directed transition between two states.
    """
    source: str
    target: str
    event: str
    guard: str | None = None
    action: str | None = None

    def __post_init__(self) -> None:
        if not self.source or not self.source.strip():
            raise ValueError("Transition source must be a non-empty string.")
        if not self.target or not self.target.strip():
            raise ValueError("Transition target must be a non-empty string.")
        if not self.event or not self.event.strip():
            raise ValueError("Transition event must be a non-empty string.")