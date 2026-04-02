"""Abstract interfaces for WebDoom server architecture"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class GameEvent:
    type: str
    data: Dict[str, Any] = None


class ISystem(ABC):
    """Base interface for all game systems"""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update system state for given delta time"""
        pass

    def on_event(self, event: GameEvent) -> None:
        """Handle game events"""
        pass


class IPhysics(ABC):
    """Physics engine interface"""

    @abstractmethod
    def is_wall(self, x: float, y: float) -> bool:
        """Check if position is a wall"""
        pass

    @abstractmethod
    def has_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if there's line of sight between two points"""
        pass

    @abstractmethod
    def cast_ray(self, ray_angle: float, player_x: float, player_y: float) -> dict:
        """Cast a ray and return distance and wall info"""
        pass


class IMap(ABC):
    """Map interface"""

    @abstractmethod
    def get_tile(self, x: int, y: int) -> str:
        """Get tile at position"""
        pass

    @abstractmethod
    def is_wall(self, x: float, y: float) -> bool:
        """Check if position is a wall"""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass


class IEntity(ABC):
    """Base entity interface"""

    @property
    @abstractmethod
    def x(self) -> float:
        pass

    @property
    @abstractmethod
    def y(self) -> float:
        pass


class IPlayer(IEntity):
    """Player entity interface"""

    @property
    @abstractmethod
    def health(self) -> int:
        pass

    @property
    @abstractmethod
    def angle(self) -> float:
        pass

    @property
    @abstractmethod
    def attack_cooldown(self) -> float:
        pass


class IEnemy(IEntity):
    """Enemy entity interface"""

    @property
    @abstractmethod
    def health(self) -> int:
        pass

    @property
    @abstractmethod
    def state(self) -> str:
        pass

    @property
    @abstractmethod
    def angle(self) -> float:
        pass


class IGameState(ABC):
    """Game state interface"""

    @abstractmethod
    def get_player(self) -> IPlayer:
        pass

    @abstractmethod
    def get_enemies(self) -> List[IEnemy]:
        pass

    @abstractmethod
    def get_game_state(self) -> str:
        pass


class IEventDispatcher(ABC):
    """Event dispatcher interface"""

    @abstractmethod
    def emit(self, event: GameEvent) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: str, callback) -> None:
        pass
