from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .state import State
from .transition import Transition


@dataclass(slots=True)
class StateMachine:
    """
    Minimal formal state machine model.

    The model is the source of truth:
    - states are nodes
    - transitions are directed labeled edges
    - one state is current during execution
    """
    name: str
    states: dict[str, State] = field(default_factory=dict)
    transitions: list[Transition] = field(default_factory=list)
    current_state: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("StateMachine name must be a non-empty string.")

        self._validate_unique_initial_state()

        if self.current_state is None:
            initial_state = self.get_initial_state()
            if initial_state is not None:
                self.current_state = initial_state.name

    def add_state(self, state: State) -> None:
        if state.name in self.states:
            raise ValueError(f"State '{state.name}' already exists.")

        if state.is_initial:
            existing_initial = self.get_initial_state()
            if existing_initial is not None:
                raise ValueError(
                    f"Initial state already exists: '{existing_initial.name}'."
                )

        self.states[state.name] = state

        if state.is_initial and self.current_state is None:
            self.current_state = state.name

    def add_states(self, states: Iterable[State]) -> None:
        for state in states:
            self.add_state(state)

    def add_transition(self, transition: Transition) -> None:
        if transition.source not in self.states:
            raise ValueError(
                f"Transition source state '{transition.source}' does not exist."
            )
        if transition.target not in self.states:
            raise ValueError(
                f"Transition target state '{transition.target}' does not exist."
            )

        self.transitions.append(transition)

    def add_transitions(self, transitions: Iterable[Transition]) -> None:
        for transition in transitions:
            self.add_transition(transition)

    def get_state(self, state_name: str) -> State:
        try:
            return self.states[state_name]
        except KeyError as exc:
            raise ValueError(f"State '{state_name}' does not exist.") from exc

    def get_initial_state(self) -> State | None:
        for state in self.states.values():
            if state.is_initial:
                return state
        return None

    def get_final_states(self) -> list[State]:
        return [state for state in self.states.values() if state.is_final]

    def get_outgoing_transitions(self, state_name: str) -> list[Transition]:
        self.get_state(state_name)
        return [t for t in self.transitions if t.source == state_name]

    def get_incoming_transitions(self, state_name: str) -> list[Transition]:
        self.get_state(state_name)
        return [t for t in self.transitions if t.target == state_name]

    def trigger(self, event: str) -> Transition:
        """
        Move from the current state using the first transition whose event matches.

        For now, guards are stored as text only and are not evaluated.
        Later, you can replace this with real predicate logic.
        """
        if self.current_state is None:
            raise RuntimeError("State machine has no current state.")

        candidates = [
            transition
            for transition in self.get_outgoing_transitions(self.current_state)
            if transition.event == event
        ]

        if not candidates:
            raise ValueError(
                f"No transition found from state '{self.current_state}' "
                f"for event '{event}'."
            )

        chosen = candidates[0]
        self.current_state = chosen.target
        return chosen

    def reset(self) -> None:
        initial_state = self.get_initial_state()
        if initial_state is None:
            raise RuntimeError("State machine has no initial state.")
        self.current_state = initial_state.name

    def is_in_final_state(self) -> bool:
        if self.current_state is None:
            return False
        return self.states[self.current_state].is_final

    def validate(self) -> list[str]:
        """
        Returns a list of validation errors.
        Empty list means the model is structurally valid enough for now.
        """
        errors: list[str] = []

        initial_states = [state.name for state in self.states.values() if state.is_initial]
        if len(initial_states) == 0:
            errors.append("State machine must have exactly one initial state, found none.")
        elif len(initial_states) > 1:
            errors.append(
                f"State machine must have exactly one initial state, found {len(initial_states)}."
            )

        for transition in self.transitions:
            if transition.source not in self.states:
                errors.append(
                    f"Transition source '{transition.source}' does not exist."
                )
            if transition.target not in self.states:
                errors.append(
                    f"Transition target '{transition.target}' does not exist."
                )

        return errors

    def summary(self) -> str:
        lines: list[str] = [
            f"StateMachine: {self.name}",
            f"Current state: {self.current_state}",
            "States:",
        ]

        for state in self.states.values():
            flags: list[str] = []
            if state.is_initial:
                flags.append("initial")
            if state.is_final:
                flags.append("final")

            suffix = f" ({', '.join(flags)})" if flags else ""
            lines.append(f"  - {state.name}{suffix}")

        lines.append("Transitions:")
        for transition in self.transitions:
            label_parts = [transition.event]
            if transition.guard:
                label_parts.append(f"[{transition.guard}]")
            if transition.action:
                label_parts.append(f"/ {transition.action}")

            label = " ".join(label_parts)
            lines.append(
                f"  - {transition.source} -> {transition.target} : {label}"
            )

        return "\n".join(lines)

    def _validate_unique_initial_state(self) -> None:
        initial_count = sum(1 for state in self.states.values() if state.is_initial)
        if initial_count > 1:
            raise ValueError(
                f"State machine must have at most one initial state, found {initial_count}."
            )

    def drawMachine(self) -> str:
        """
        Returns a simple ASCII drawing of the state machine.

        This is not a full graph layout engine.
        It prints:
        - the initial state
        - each state's outgoing transitions
        - marks final states
        """
        lines: list[str] = []
        initial_state = self.get_initial_state()

        lines.append(f"STATE MACHINE: {self.name}")
        lines.append("=" * (15 + len(self.name)))

        if initial_state is not None:
            lines.append(f"START --> [{initial_state.name}]")
        else:
            lines.append("START --> [None]")

        lines.append("")

        for state in self.states.values():
            state_label = state.name
            markers: list[str] = []

            if state.is_initial:
                markers.append("initial")
            if state.is_final:
                markers.append("final")

            if markers:
                state_label += f" ({', '.join(markers)})"

            lines.append(f"[{state_label}]")

            outgoing = self.get_outgoing_transitions(state.name)
            if not outgoing:
                lines.append("  -- no outgoing transitions --")
            else:
                for transition in outgoing:
                    edge_label_parts = [transition.event]

                    if transition.guard:
                        edge_label_parts.append(f"[{transition.guard}]")
                    if transition.action:
                        edge_label_parts.append(f"/ {transition.action}")

                    edge_label = " ".join(edge_label_parts)
                    lines.append(f"  |")
                    lines.append(f"  +-- {edge_label} --> [{transition.target}]")

            lines.append("")

        final_states = self.get_final_states()
        if final_states:
            lines.append("END STATES:")
            for state in final_states:
                lines.append(f"  --> [{state.name}]")

        return "\n".join(lines)
        