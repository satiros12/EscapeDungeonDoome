"""Entity Factory - Factory pattern for game entities"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import random

from game_state import Player, Enemy, Corpse, HitEffect, GameConfig
from core.event_system import EventType, EventDispatcher


class EnemyType(Enum):
    IMP = "imp"
    DEMON = "demon"
    CACODEMON = "cacodemon"


class WeaponType(Enum):
    FISTS = "fists"
    CHAINSAW = "chainsaw"
    SHOTGUN = "shotgun"
    CHAINGUN = "chaingun"


@dataclass
class EnemyConfig:
    health: int = 30
    speed: float = 2.5
    damage: int = 10
    attack_range: float = 1.0
    attack_cooldown: float = 1.0
    detection_range: float = 5.0
    patrol_speed: float = 1.0
    behavior: str = "chase"


@dataclass  
class WeaponConfig:
    damage: int = 10
    range: float = 1.5
    cooldown: float = 0.5
    projectile: bool = False
    pellets: int = 1


ENEMY_CONFIGS: Dict[EnemyType, EnemyConfig] = {
    EnemyType.IMP: EnemyConfig(
        health=30,
        speed=2.5,
        damage=10,
        attack_range=1.0,
        attack_cooldown=1.0,
        detection_range=5.0,
        patrol_speed=1.0,
        behavior="chase"
    ),
    EnemyType.DEMON: EnemyConfig(
        health=60,
        speed=2.0,
        damage=15,
        attack_range=1.2,
        attack_cooldown=1.5,
        detection_range=6.0,
        patrol_speed=0.8,
        behavior="flanker"
    ),
    EnemyType.CACODEMON: EnemyConfig(
        health=100,
        speed=1.5,
        damage=20,
        attack_range=3.0,
        attack_cooldown=2.0,
        detection_range=8.0,
        patrol_speed=0.5,
        behavior="shooter"
    ),
}


WEAPON_CONFIGS: Dict[WeaponType, WeaponConfig] = {
    WeaponType.FISTS: WeaponConfig(
        damage=10,
        range=1.5,
        cooldown=0.5,
        projectile=False,
        pellets=1
    ),
    WeaponType.CHAINSAW: WeaponConfig(
        damage=25,
        range=1.5,
        cooldown=0.2,
        projectile=False,
        pellets=1
    ),
    WeaponType.SHOTGUN: WeaponConfig(
        damage=10,
        range=8.0,
        cooldown=1.0,
        projectile=True,
        pellets=8
    ),
    WeaponType.CHAINGUN: WeaponConfig(
        damage=8,
        range=15.0,
        cooldown=0.1,
        projectile=True,
        pellets=1
    ),
}


class EntityFactory:
    def __init__(self, event_dispatcher: Optional[EventDispatcher] = None):
        self.event_dispatcher = event_dispatcher
        self._entity_counter = 0

    def create_player(self, x: float = 1.5, y: float = 1.5) -> Player:
        return Player(x=x, y=y, angle=0.0)

    def create_enemy(
        self, 
        x: float, 
        y: float, 
        enemy_type: EnemyType = EnemyType.IMP
    ) -> Enemy:
        self._entity_counter += 1
        config = ENEMY_CONFIGS[enemy_type]
        
        enemy = Enemy(
            x=x,
            y=y,
            angle=0.0,
            health=config.health,
            state="patrol",
            patrol_dir=random.random() * 2 * 3.14159,
        )
        
        if self.event_dispatcher:
            from core.event_system import GameEvent
            self.event_dispatcher.emit(GameEvent(
                type=EventType.ENEMY_SPAWN,
                data={"enemy": enemy, "enemy_type": enemy_type.value}
            ))
        
        return enemy

    def create_corpse(self, x: float, y: float) -> Corpse:
        return Corpse(x=x, y=y)

    def create_hit_effect(self, x: float, y: float) -> HitEffect:
        return HitEffect(x=x, y=y, timer=0.3)

    def parse_map_spawns(self, map_data: List[str]) -> Dict[str, List[tuple]]:
        spawns = {"player": None, "enemies": []}
        
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == "P":
                    spawns["player"] = (x + 0.5, y + 0.5)
                elif char == "E":
                    spawns["enemies"].append((x + 0.5, y + 0.5))
        
        return spawns

    def create_enemies_from_map(
        self, 
        map_data: List[str],
        enemy_type: EnemyType = EnemyType.IMP
    ) -> List[Enemy]:
        spawns = self.parse_map_spawns(map_data)
        enemies = []
        
        for x, y in spawns["enemies"]:
            enemy = self.create_enemy(x, y, enemy_type)
            enemies.append(enemy)
        
        return enemies


class WeaponFactory:
    def __init__(self):
        self.current_weapon = WeaponType.FISTS

    def get_weapon_config(self, weapon_type: WeaponType = None) -> WeaponConfig:
        if weapon_type is None:
            weapon_type = self.current_weapon
        return WEAPON_CONFIGS[weapon_type]

    def set_weapon(self, weapon_type: WeaponType) -> None:
        self.current_weapon = weapon_type

    def get_available_weapons(self) -> List[WeaponType]:
        return list(WEAPON_CONFIGS.keys())
