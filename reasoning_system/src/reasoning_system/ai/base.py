from abc import ABC, abstractmethod

from .schemas import ExtractionResult


class BaseAIClient(ABC):
    @abstractmethod
    def extract_atomic_facts(self, text: str) -> ExtractionResult:
        """Extract atomic reasoning facts from the input text."""
        raise NotImplementedError