"""
Weapon System - handles different weapon types and combat
"""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from engine.game_state import GameState, Enemy


@dataclass
class DamageResult:
    """Result of a weapon attack."""

    damage: int
    hit_count: int
    killed: bool
    target: Optional[Enemy] = None


class Weapon(ABC):
    """Abstract base class for weapons."""

    @abstractmethod
    def get_name(self) -> str:
        """Get weapon name."""
        pass

    @abstractmethod
    def get_damage(self) -> int:
        """Get weapon damage."""
        pass

    @abstractmethod
    def get_range(self) -> float:
        """Get weapon range."""
        pass

    @abstractmethod
    def get_cooldown(self) -> float:
        """Get weapon attack cooldown."""
        pass

    @abstractmethod
    def is_projectile(self) -> bool:
        """Check if weapon is a projectile weapon."""
        pass

    @abstractmethod
    def get_pellets(self) -> int:
        """Get number of pellets (for shotgun)."""
        pass

    @abstractmethod
    def fire(
        self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy
    ) -> DamageResult:
        """Fire the weapon at a target."""
        pass


class MeleeWeapon(Weapon):
    """Melee weapon implementation."""

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

    def fire(
        self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy
    ) -> DamageResult:
        target.health -= self._damage
        killed = target.health <= 0
        return DamageResult(
            damage=self._damage, hit_count=1, killed=killed, target=target
        )


class ProjectileWeapon(Weapon):
    """Projectile weapon implementation (shotgun, chaingun)."""

    def __init__(
        self, name: str, damage: int, range: float, cooldown: float, pellets: int = 1
    ):
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

    def fire(
        self, attacker_x: float, attacker_y: float, attacker_angle: float, target: Enemy
    ) -> DamageResult:
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
            damage=total_damage, hit_count=hits, killed=killed, target=target
        )


class WeaponSystem:
    """Manages all weapons in the game."""

    WEAPONS = {
        "fists": MeleeWeapon("Fists", 10, 1.5, 0.5),
        "chainsaw": MeleeWeapon("Chainsaw", 25, 1.5, 0.2),
        "shotgun": ProjectileWeapon("Shotgun", 10, 8.0, 1.0, 8),
        "chaingun": ProjectileWeapon("Chaingun", 8, 15.0, 0.1, 1),
    }

    def __init__(self, state: GameState):
        self.state = state
        self.current_weapon = "fists"

    def set_weapon(self, weapon_name: str) -> bool:
        """Set current weapon."""
        if weapon_name in self.WEAPONS:
            self.current_weapon = weapon_name
            return True
        return False

    def get_current_weapon(self) -> Weapon:
        """Get the current weapon."""
        return self.WEAPONS.get(self.current_weapon, self.WEAPONS["fists"])

    def get_available_weapons(self) -> List[str]:
        """Get list of available weapon names."""
        return list(self.WEAPONS.keys())

    def player_attack(self) -> List[DamageResult]:
        """Player attacks with current weapon."""
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

                from engine.game_state import HitEffect

                self.state.hit_effects.append(HitEffect(x=enemy.x, y=enemy.y))

                if result.killed:
                    enemy.state = "dying"
                    enemy.dying_progress = 0

        return results
