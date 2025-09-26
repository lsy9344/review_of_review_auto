"""State machine definitions for orchestrating the app run lifecycle."""


class OrchestratorState:  # placeholder
    """Represents the orchestrator state. To be implemented."""

    def __init__(self) -> None:
        self.phase = "idle"

    def set_phase(self, phase: str) -> None:
        self.phase = phase
