from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class State:
    """
    Represents a single state in a state machine.
    """
    name: str
    is_initial: bool = False
    is_final: bool = False

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("State name must be a non-empty string.")
