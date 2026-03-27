"""Combat system"""

import math
from systems.base import SystemBase, GameEvent
from game_state import GameState, GameConfig, Enemy, Corpse, HitEffect


class CombatSystem(SystemBase):
    """Handles combat mechanics"""

    def __init__(self, state: GameState):
        super().__init__()
        self.state = state

    def update(self, dt: float) -> None:
        if self.state.game_state != "playing":
            return

        self._update_dying_enemies(dt)
        self._update_hit_effects(dt)
        self._check_conditions()

    def player_attack(self) -> None:
        """Player attacks nearby enemies"""
        if self.state.player.attack_cooldown > 0:
            return

        self.state.player.attack_cooldown = GameConfig.ATTACK_COOLDOWN
        player = self.state.player

        for enemy in self.state.enemies:
            if enemy.state in ("dying", "dead"):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < GameConfig.ATTACK_RANGE:
                enemy.health -= GameConfig.PLAYER_DAMAGE
                self.state.hit_effects.append(HitEffect(x=enemy.x, y=enemy.y))

                if enemy.health <= 0:
                    enemy.state = "dying"
                    enemy.dying_progress = 0

    def _update_dying_enemies(self, dt: float) -> None:
        for enemy in self.state.enemies:
            if enemy.state == "dying":
                enemy.dying_progress += dt
                if enemy.dying_progress >= 1:
                    enemy.state = "dead"
                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1

    def _update_hit_effects(self, dt: float) -> None:
        for effect in self.state.hit_effects[:]:
            effect.timer -= dt
            if effect.timer <= 0:
                self.state.hit_effects.remove(effect)

    def _check_conditions(self) -> None:
        alive_enemies = [e for e in self.state.enemies if e.state != "dead"]
        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
