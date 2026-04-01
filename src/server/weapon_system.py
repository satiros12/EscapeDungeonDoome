"""Weapon system for WebDoom - manages player weapons and combat"""

from dataclasses import dataclass
from typing import Dict, Optional, List
import math
import random


class WeaponType:
    """Weapon type identifiers"""

    FISTS = "fists"
    CHAINSAW = "chainsaw"
    SHOTGUN = "shotgun"
    CHAINGUN = "chaingun"


@dataclass
class Weapon:
    """Weapon data class"""

    name: str
    damage: int
    range: float
    cooldown: float
    projectile: bool = False
    pellets: int = 1
    ammo_type: str = "none"
    max_ammo: int = -1

    def __post_init__(self):
        if self.ammo_type == "none":
            self.max_ammo = -1


class WeaponSystem:
    """Manages player weapons and combat calculations"""

    WEAPONS = {
        "fists": Weapon("Fists", 10, 1.5, 0.5),
        "chainsaw": Weapon("Chainsaw", 25, 1.5, 0.2),
        "shotgun": Weapon("Shotgun", 10, 8.0, 1.0, True, 8, "shotgun"),
        "chaingun": Weapon("Chaingun", 8, 15.0, 0.1, True, 1, "chaingun"),
    }

    def __init__(self, state):
        self.state = state
        self.current_weapon = "fists"

    def set_weapon(self, weapon_name: str) -> bool:
        """Set current weapon if valid and player has ammo"""
        if weapon_name not in self.WEAPONS:
            return False

        weapon = self.WEAPONS[weapon_name]

        # Check ammo for weapons that need it
        if weapon.ammo_type != "none":
            ammo = self.state.player.ammo.get(weapon.ammo_type, 0)
            if ammo <= 0:
                return False

        self.current_weapon = weapon_name
        self.state.player.current_weapon = weapon_name
        return True

    def get_current_weapon(self) -> Weapon:
        """Get the current weapon object"""
        return self.WEAPONS.get(self.current_weapon, self.WEAPONS["fists"])

    def get_available_weapons(self) -> List[str]:
        """Get list of available weapon names"""
        return list(self.WEAPONS.keys())

    def has_weapon(self, weapon_name: str) -> bool:
        """Check if player has a specific weapon"""
        return weapon_name in self.WEAPONS

    def get_ammo(self, ammo_type: str) -> int:
        """Get ammo count for a specific ammo type"""
        return self.state.player.ammo.get(ammo_type, 0)

    def consume_ammo(self, ammo_type: str, amount: int = 1) -> bool:
        """Consume ammo, returns True if successful"""
        if ammo_type == "none":
            return True

        current = self.state.player.ammo.get(ammo_type, 0)
        if current >= amount:
            self.state.player.ammo[ammo_type] = current - amount
            return True
        return False

    def player_attack(self) -> Dict:
        """Execute attack with current weapon, returns attack info"""
        if self.state.player.attack_cooldown > 0:
            return {"success": False, "reason": "cooldown"}

        weapon = self.get_current_weapon()

        # Check ammo for projectile weapons
        if weapon.projectile:
            if not self.consume_ammo(weapon.ammo_type):
                return {"success": False, "reason": "no_ammo"}

        # Set cooldown
        self.state.player.attack_cooldown = weapon.cooldown

        # Calculate damage based on weapon type
        hits = []
        player = self.state.player

        if weapon.projectile:
            # Projectile weapons (shotgun, chaingun) - multiple pellets
            for pellet in range(weapon.pellets):
                # Add some spread to pellets
                spread_angle = random.uniform(-0.3, 0.3)
                check_angle = player.angle + spread_angle

                # Check each enemy
                for enemy in self.state.enemies:
                    if enemy.state in ("dying", "dead"):
                        continue

                    dx = enemy.x - player.x
                    dy = enemy.y - player.y
                    dist = math.sqrt(dx * dx + dy * dy)

                    if dist < weapon.range:
                        # Check angle to enemy
                        angle_to_enemy = math.atan2(dy, dx)
                        angle_diff = abs(
                            self._normalize_angle(angle_to_enemy - check_angle)
                        )

                        # Pellet hit if within 30 degree cone
                        if angle_diff < math.pi / 6:
                            damage = weapon.damage
                            enemy.health -= damage
                            hits.append(
                                {
                                    "enemy_index": self.state.enemies.index(enemy),
                                    "x": enemy.x,
                                    "y": enemy.y,
                                    "damage": damage,
                                }
                            )

                            if enemy.health <= 0:
                                enemy.state = "dying"
                                enemy.dying_progress = 0
        else:
            # Melee weapons (fists, chainsaw)
            for enemy in self.state.enemies:
                if enemy.state in ("dying", "dead"):
                    continue

                dx = enemy.x - player.x
                dy = enemy.y - player.y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < weapon.range:
                    enemy.health -= weapon.damage
                    hits.append(
                        {
                            "enemy_index": self.state.enemies.index(enemy),
                            "x": enemy.x,
                            "y": enemy.y,
                            "damage": weapon.damage,
                        }
                    )

                    if enemy.health <= 0:
                        enemy.state = "dying"
                        enemy.dying_progress = 0

        return {"success": True, "weapon": self.current_weapon, "hits": hits}

    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-PI, PI]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
