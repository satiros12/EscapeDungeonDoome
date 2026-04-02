"""
Combat System - handles combat mechanics and damage
"""

import math
from systems.base import SystemBase, GameEvent
from engine.game_state import GameState, Enemy, Corpse, HitEffect


class CombatSystem(SystemBase):
    """Handles combat mechanics."""

    def __init__(self, state: GameState):
        super().__init__()
        self.state = state
        self.attack_range = 1.5
        self.attack_damage = 10
        self.attack_cooldown = 0.5

    def update(self, dt: float) -> None:
        """Update combat state."""
        if self.state.game_state != "playing":
            return

        self._update_dying_enemies(dt)
        self._update_hit_effects(dt)
        self._check_win_condition()

    def player_attack(self) -> None:
        """Player attacks nearby enemies."""
        if self.state.player.attack_cooldown > 0:
            return

        self.state.player.attack_cooldown = self.attack_cooldown
        player = self.state.player

        for enemy in self.state.enemies:
            if enemy.state in ("dying", "dead"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.attack_range:
                enemy.health -= self.attack_damage
                self.state.hit_effects.append(HitEffect(x=enemy.x, y=enemy.y))

                if enemy.health <= 0:
                    enemy.state = "dying"
                    enemy.dying_progress = 0

    def _update_dying_enemies(self, dt: float) -> None:
        """Update dying enemy animations."""
        for enemy in self.state.enemies:
            if enemy.state == "dying":
                enemy.dying_progress += dt
                if enemy.dying_progress >= 1.0:
                    enemy.state = "dead"
                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1

    def _update_hit_effects(self, dt: float) -> None:
        """Update hit effect timers."""
        for effect in self.state.hit_effects[:]:
            effect.timer -= dt
            if effect.timer <= 0:
                self.state.hit_effects.remove(effect)

    def _check_win_condition(self) -> None:
        """Check if player has won the game."""
        alive_enemies = [e for e in self.state.enemies if e.state != "dead"]
        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
