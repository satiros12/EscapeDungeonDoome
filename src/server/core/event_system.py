"""Event System - Event dispatcher for game events"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class EventType(Enum):
    PLAYER_MOVE = "player_move"
    PLAYER_ATTACK = "player_attack"
    PLAYER_DAMAGED = "player_damaged"
    PLAYER_DEATH = "player_death"
    ENEMY_SPAWN = "enemy_spawn"
    ENEMY_SIGHT = "enemy_sight"
    ENEMY_ATTACK = "enemy_attack"
    ENEMY_DAMAGED = "enemy_damaged"
    ENEMY_DEATH = "enemy_death"
    ENEMY_STATE_CHANGE = "enemy_state_change"
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_PAUSE = "game_pause"
    GAME_RESUME = "game_resume"
    WEAPON_FIRE = "weapon_fire"
    WEAPON_HIT = "weapon_hit"
    ITEM_PICKUP = "item_pickup"


@dataclass
class GameEvent:
    type: EventType
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"


class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._event_queue: List[GameEvent] = []
        self._global_listeners: List[Callable] = []

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        if event_type in self._listeners:
            self._listeners[event_type] = [
                cb for cb in self._listeners[event_type] if cb != callback
            ]

    def subscribe_global(self, callback: Callable) -> None:
        self._global_listeners.append(callback)

    def unsubscribe_global(self, callback: Callable) -> None:
        self._global_listeners = [
            cb for cb in self._global_listeners if cb != callback
        ]

    def emit(self, event: GameEvent) -> None:
        self._event_queue.append(event)

    def emit_now(self, event: GameEvent) -> None:
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:
                callback(event)

        for callback in self._global_listeners:
            callback(event)

    def process_queue(self) -> None:
        while self._event_queue:
            event = self._event_queue.pop(0)
            self.emit_now(event)

    def clear(self) -> None:
        self._listeners.clear()
        self._event_queue.clear()
        self._global_listeners.clear()

    def get_listener_count(self, event_type: EventType = None) -> int:
        if event_type:
            return len(self._listeners.get(event_type, []))
        return sum(len(listeners) for listeners in self._listeners.values())


class EventLogger:
    def __init__(self, dispatcher: EventDispatcher):
        self.dispatcher = dispatcher
        self.log: List[GameEvent] = []
        dispatcher.subscribe_global(self._log_event)

    def _log_event(self, event: GameEvent) -> None:
        self.log.append(event)
        if len(self.log) > 1000:
            self.log = self.log[-1000:]

    def get_events(self, event_type: EventType = None, limit: int = 100) -> List[GameEvent]:
        if event_type:
            return [e for e in self.log if e.type == event_type][-limit:]
        return self.log[-limit:]

    def clear(self) -> None:
        self.log.clear()
