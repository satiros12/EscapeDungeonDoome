"""Base system class for WebDoom"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class GameEvent:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


class ISystem(ABC):
    """Base interface for all game systems"""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update system state for given delta time"""
        pass

    def on_event(self, event: GameEvent) -> None:
        """Handle game events"""
        pass


class SystemBase(ISystem):
    """Base class for all systems with common functionality"""

    def __init__(self):
        self._events = []

    def update(self, dt: float) -> None:
        raise NotImplementedError("Subclasses must implement update()")

    def on_event(self, event: GameEvent) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()
