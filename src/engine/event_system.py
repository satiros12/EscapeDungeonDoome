"""
Event System - handles game events and event dispatching
"""

from enum import Enum
from typing import Dict, List, Callable, Any
from dataclasses import dataclass


class EventType(Enum):
    """Event type constants."""

    GAME_START = "game_start"
    GAME_WIN = "game_win"
    GAME_OVER = "game_over"
    PLAYER_DEATH = "player_death"
    PLAYER_DAMAGE = "player_damage"
    ENEMY_DEATH = "enemy_death"
    ENEMY_HIT = "enemy_hit"
    ITEM_PICKUP = "item_pickup"
    WEAPON_FIRE = "weapon_fire"
    WEAPON_HIT = "weapon_hit"
    MAP_CHANGE = "map_change"
    CONSOLE_COMMAND = "console_command"
    ENTITY_CREATED = "entity_created"
    ENTITY_DESTROYED = "entity_destroyed"
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"


@dataclass
class GameEvent:
    """Represents a game event."""

    type: EventType
    data: Dict[str, Any]


class EventListener:
    """Represents a listener for a specific event type."""

    def __init__(self, callback: Callable, event_type: EventType):
        self.callback = callback
        self.event_type = event_type


class EventSystem:
    """Central event dispatcher for the game."""

    def __init__(self):
        self._listeners: Dict[EventType, List[EventListener]] = {}
        self._event_queue: List[GameEvent] = []

    def subscribe(self, event_type: EventType, callback: Callable) -> EventListener:
        """Subscribe to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        listener = EventListener(callback, event_type)
        self._listeners[event_type].append(listener)
        return listener

    def unsubscribe(self, listener: EventListener) -> None:
        """Unsubscribe from an event."""
        if listener.event_type in self._listeners:
            self._listeners[listener.event_type].remove(listener)

    def emit(self, event_type: EventType, data: Dict[str, Any] = None) -> None:
        """Emit an event."""
        if data is None:
            data = {}

        event = GameEvent(type=event_type, data=data)
        self._event_queue.append(event)

    def process_events(self) -> None:
        """Process all queued events."""
        while self._event_queue:
            event = self._event_queue.pop(0)
            self._dispatch_event(event)

    def _dispatch_event(self, event: GameEvent) -> None:
        """Dispatch an event to all listeners."""
        if event.type in self._listeners:
            for listener in self._listeners[event.type]:
                try:
                    listener.callback(event)
                except Exception as e:
                    print(f"Error in event listener: {e}")

    def clear(self) -> None:
        """Clear all listeners and queued events."""
        self._listeners.clear()
        self._event_queue.clear()


# Global event system instance
_global_event_system: EventSystem = None


def get_event_system() -> EventSystem:
    """Get the global event system instance."""
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = EventSystem()
    return _global_event_system
