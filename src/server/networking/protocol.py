"""Network Protocol - Delta compression and message handling"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy


class MessageType(Enum):
    INPUT = "input"
    ACTION = "action"
    STATE = "state"
    EVENT = "event"
    SYNC = "sync"
    CHAT = "chat"


class StateMode(Enum):
    FULL = "full"
    DELTA = "delta"


@dataclass
class GameStateMessage:
    type: str = "state"
    timestamp: float = field(default_factory=time.time)
    mode: str = "full"
    data: Dict[str, Any] = field(default_factory=dict)


class DeltaState:
    def __init__(self):
        self._previous_state: Dict[str, Any] = {}
        self._current_state: Dict[str, Any] = {}

    def update(self, new_state: Dict[str, Any]) -> Dict[str, Any]:
        self._previous_state = copy.deepcopy(self._current_state)
        self._current_state = copy.deepcopy(new_state)
        
        if not self._previous_state:
            return {"mode": "full", "data": new_state}
        
        return self._compute_delta()

    def _compute_delta(self) -> Dict[str, Any]:
        changes = {}
        removed = []
        
        self._find_changes(self._current_state, self._previous_state, "", changes)
        self._find_removed(self._previous_state, self._current_state, "", removed)
        
        return {
            "mode": "delta",
            "changes": changes,
            "removed": removed,
            "timestamp": time.time()
        }

    def _find_changes(self, current: Any, previous: Any, prefix: str, changes: Dict) -> None:
        if isinstance(current, dict) and isinstance(previous, dict):
            for key in current:
                new_prefix = f"{prefix}.{key}" if prefix else key
                if key not in previous:
                    changes[new_prefix] = current[key]
                elif current[key] != previous[key]:
                    if isinstance(current[key], dict):
                        self._find_changes(current[key], previous[key], new_prefix, changes)
                    else:
                        changes[new_prefix] = current[key]
        elif current != previous:
            changes[prefix] = current

    def _find_removed(self, previous: Any, current: Any, prefix: str, removed: List) -> None:
        if isinstance(previous, dict):
            for key in previous:
                new_prefix = f"{prefix}.{key}" if prefix else key
                if key not in current:
                    removed.append(new_prefix)
                elif isinstance(previous[key], dict):
                    self._find_removed(previous[key], current.get(key, {}), new_prefix, removed)

    def get_current_state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._current_state)


class StateCompressor:
    @staticmethod
    def compress_player(player: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "x": round(player.get("x", 0), 2),
            "y": round(player.get("y", 0), 2),
            "angle": round(player.get("angle", 0), 3),
            "health": player.get("health", 100),
        }

    @staticmethod
    def compress_enemy(enemy: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "x": round(enemy.get("x", 0), 2),
            "y": round(enemy.get("y", 0), 2),
            "angle": round(enemy.get("angle", 0), 3),
            "health": enemy.get("health", 30),
            "state": enemy.get("state", "patrol"),
        }
        
        if enemy.get("dying_progress", 0) > 0:
            result["dying_progress"] = round(enemy.get("dying_progress", 0), 2)
        if enemy.get("attack_cooldown", 0) > 0:
            result["attack_cooldown"] = round(enemy.get("attack_cooldown", 0), 2)
            
        return result

    @staticmethod
    def compress_state(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "game_state": state.get("game_state", "menu"),
            "player": StateCompressor.compress_player(state.get("player", {})),
            "enemies": [StateCompressor.compress_enemy(e) for e in state.get("enemies", [])],
            "corpses": state.get("corpses", []),
            "kills": state.get("kills", 0),
            "hit_effects": state.get("hit_effects", []),
        }


class NetworkProtocol:
    def __init__(self):
        self.delta_state = DeltaState()
        self._last_full_state_time = 0
        self._full_state_interval = 5.0

    def create_state_message(self, state: Dict[str, Any], force_full: bool = False) -> str:
        compressed = StateCompressor.compress_state(state)
        
        should_send_full = (
            force_full or 
            time.time() - self._last_full_state_time > self._full_state_interval
        )
        
        if should_send_full:
            self._last_full_state_time = time.time()
            message = GameStateMessage(
                type="state",
                timestamp=time.time(),
                mode="full",
                data=compressed
            )
        else:
            delta = self.delta_state.update(compressed)
            message = GameStateMessage(
                type="state",
                timestamp=time.time(),
                mode="delta",
                data=delta
            )
        
        return json.dumps(asdict(message))

    def parse_client_message(self, data: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    def create_event_message(self, event_type: str, event_data: Dict[str, Any]) -> str:
        message = {
            "type": "event",
            "event": event_type,
            "data": event_data,
            "timestamp": time.time()
        }
        return json.dumps(message)

    def create_sync_message(self) -> str:
        message = {
            "type": "sync",
            "timestamp": time.time()
        }
        return json.dumps(message)


def serialize_message(msg_type: MessageType, data: Any) -> str:
    message = {
        "type": msg_type.value,
        "timestamp": time.time(),
        "data": data if isinstance(data, dict) else {"value": data}
    }
    return json.dumps(message)


def deserialize_message(data: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None
