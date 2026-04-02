"""Weapon System - Combat mechanics with different weapon types"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math
import random

from game_state import GameState, GameConfig, Enemy, HitEffect
from core.event_system import EventType, EventDispatcher


@dataclass
class DamageResult:
    damage: int
    hit_count: int
    killed: bool
    target: Optional[Enemy] = None


class Weapon(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_damage(self) -> int:
        pass

    @abstractmethod
    def get_range(self) -> float:
        pass

    @abstractmethod
    def get_cooldown(self) -> float:
        pass

    @abstractmethod
    def is_projectile(self) -> bool:
        pass

    @abstractmethod
    def get_pellets(self) -> int:
        pass

    @abstractmethod
    def fire(self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy) -> DamageResult:
        pass


class MeleeWeapon(Weapon):
    def __init__(self, name: str, damage: int, range: float, cooldown: float):
        self._name = name
        self._damage = damage
        self._range = range
        self._cooldown = cooldown

    def get_name(self) -> str:
        return self._name

    def get_damage(self) -> int:
        return self._damage

    def get_range(self) -> float:
        return self._range

    def get_cooldown(self) -> float:
        return self._cooldown

    def is_projectile(self) -> bool:
        return False

    def get_pellets(self) -> int:
        return 1

    def fire(self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy) -> DamageResult:
        target.health -= self._damage
        killed = target.health <= 0
        return DamageResult(
            damage=self._damage,
            hit_count=1,
            killed=killed,
            target=target
        )


class ProjectileWeapon(Weapon):
    def __init__(self, name: str, damage: int, range: float, cooldown: float, pellets: int = 1):
        self._name = name
        self._damage = damage
        self._range = range
        self._cooldown = cooldown
        self._pellets = pellets

    def get_name(self) -> str:
        return self._name

    def get_damage(self) -> int:
        return self._damage

    def get_range(self) -> float:
        return self._range

    def get_cooldown(self) -> float:
        return self._cooldown

    def is_projectile(self) -> bool:
        return True

    def get_pellets(self) -> int:
        return self._pellets

    def fire(self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy) -> DamageResult:
        hits = 0
        spread = 0.3

        for _ in range(self._pellets):
            angle_offset = random.uniform(-spread, spread)
            ray_angle = attacker_angle + angle_offset

            dx = target.x - attacker_x
            dy = target.y - attacker_y
            dist = math.sqrt(dx * dx + dy * dy)
            target_angle = math.atan2(dy, dx)

            angle_diff = abs(ray_angle - target_angle)
            while angle_diff > math.pi:
                angle_diff = abs(angle_diff - 2 * math.pi)

            if angle_diff < 0.3 and dist <= self._range:
                hits += 1

        total_damage = hits * self._damage
        target.health -= total_damage
        killed = target.health <= 0

        return DamageResult(
            damage=total_damage,
            hit_count=hits,
            killed=killed,
            target=target
        )


class WeaponSystem:
    WEAPONS = {
        "fists": MeleeWeapon("Fists", 10, 1.5, 0.5),
        "chainsaw": MeleeWeapon("Chainsaw", 25, 1.5, 0.2),
        "shotgun": ProjectileWeapon("Shotgun", 10, 8.0, 1.0, 8),
        "chaingun": ProjectileWeapon("Chaingun", 8, 15.0, 0.1, 1),
    }

    def __init__(self, state: GameState, event_dispatcher: Optional[EventDispatcher] = None):
        self.state = state
        self.event_dispatcher = event_dispatcher
        self.current_weapon = "fists"

    def set_weapon(self, weapon_name: str) -> bool:
        if weapon_name in self.WEAPONS:
            self.current_weapon = weapon_name
            return True
        return False

    def get_current_weapon(self) -> Weapon:
        return self.WEAPONS.get(self.current_weapon, self.WEAPONS["fists"])

    def get_available_weapons(self) -> List[str]:
        return list(self.WEAPONS.keys())

    def player_attack(self) -> List[DamageResult]:
        player = self.state.player
        
        if player.attack_cooldown > 0:
            return []

        weapon = self.get_current_weapon()
        player.attack_cooldown = weapon.get_cooldown()

        results = []
        
        for enemy in self.state.enemies:
            if enemy.state in ("dying", "dead"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < weapon.get_range():
                result = weapon.fire(player.x, player.y, player.angle, enemy)
                results.append(result)

                self.state.hit_effects.append(HitEffect(x=enemy.x, y=enemy.y))

                if self.event_dispatcher:
                    from core.event_system import GameEvent
                    self.event_dispatcher.emit(GameEvent(
                        type=EventType.WEAPON_HIT,
                        data={
                            "weapon": weapon.get_name(),
                            "damage": result.damage,
                            "hit_count": result.hit_count,
                            "target": enemy
                        }
                    ))

                if result.killed:
                    enemy.state = "dying"
                    enemy.dying_progress = 0

                    if self.event_dispatcher:
                        self.event_dispatcher.emit(GameEvent(
                            type=EventType.ENEMY_DEATH,
                            data={"enemy": enemy}
                        ))

        return results

    def update(self, dt: float) -> None:
        if player.cooldown > 0:
            player.attack_cooldown -= dt


class Item(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def apply(self, target) -> bool:
        pass


class HealthItem(Item):
    def __init__(self, heal_amount: int = 25):
        self.heal_amount = heal_amount

    def get_name(self) -> str:
        return f"Health Pack +{self.heal_amount}"

    def get_type(self) -> str:
        return "health"

    def apply(self, target) -> bool:
        if hasattr(target, 'health'):
            old_health = target.health
            target.health = min(100, target.health + self.heal_amount)
            return target.health > old_health
        return False


class AmmoItem(Item):
    def __init__(self, weapon_name: str, ammo_amount: int = 10):
        self.weapon_name = weapon_name
        self.ammo_amount = ammo_amount

    def get_name(self) -> str:
        return f"{self.weapon_name} ammo +{self.ammo_amount}"

    def get_type(self) -> str:
        return "ammo"

    def apply(self, target) -> bool:
        if hasattr(target, 'ammo') and hasattr(target, 'current_weapon'):
            if self.weapon_name == target.current_weapon:
                target.ammo = getattr(target, 'ammo', 0) + self.ammo_amount
                return True
        return False


class ItemSystem:
    def __init__(self, state: GameState, event_dispatcher: Optional[EventDispatcher] = None):
        self.state = state
        self.event_dispatcher = event_dispatcher
        self.items: List[Tuple[float, float, Item]] = []

    def add_item(self, x: float, y: float, item: Item) -> None:
        self.items.append((x, y, item))

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def check_pickup(self, player_x: float, player_y: float) -> List[Item]:
        picked = []
        pickup_range = 0.5

        for i in range(len(self.items) - 1, -1, -1):
            x, y, item = self.items[i]
            dist = math.sqrt((x - player_x) ** 2 + (y - player_y) ** 2)

            if dist < pickup_range:
                if item.apply(self.state.player):
                    picked.append(item)
                    self.items.pop(i)

                    if self.event_dispatcher:
                        from core.event_system import GameEvent
                        self.event_dispatcher.emit(GameEvent(
                            type=EventType.ITEM_PICKUP,
                            data={"item": item.get_name(), "x": x, "y": y}
                        ))

        return picked

    def spawn_items(self, map_data: List[str]) -> None:
        for y, row in enumerate(map_data):
            for x, char in enumerate(row):
                if char == "H":
                    self.add_item(x + 0.5, y + 0.5, HealthItem(25))
                elif char == "A":
                    self.add_item(x + 0.5, y + 0.5, AmmoItem("shotgun", 10))
                elif char == "C":
                    self.add_item(x + 0.5, y + 0.5, AmmoItem("chaingun", 50))
