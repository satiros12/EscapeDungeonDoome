"""Game logic for WebDoom server"""

import math
import random
from game_state import GameState, GameConfig, Enemy, Corpse, HitEffect
from physics import Physics


class GameLogic:
    def __init__(self, state: GameState):
        self.state = state
        self.physics = Physics(state)
        self.logger = None

    def set_logger(self, logger):
        """Set logger callback for events"""
        self.logger = logger

    def log(self, msg: str, level: str = "INFO"):
        """Log a message"""
        if self.logger:
            self.logger(msg, level)

    def normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-PI, PI]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def update(self, dt: float):
        """Main game update - called every frame"""
        if self.state.game_state != "playing":
            return

        self.move_player(dt, self.state.pending_input)
        self.update_enemies(dt)
        self.update_dying_enemies(dt)
        self.update_hit_effects(dt)
        self.check_conditions()

    def move_player(self, dt: float, keys: dict):
        """Update player position based on input"""
        player = self.state.player

        speed_mult = getattr(player, "speed_multiplier", 1.0) or 1.0
        speed_mult = (
            getattr(self.state, "player_speed_multiplier", speed_mult) or speed_mult
        )

        move_x = 0.0
        move_y = 0.0

        if keys.get("KeyW", False):
            move_x += math.cos(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
            move_y += math.sin(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
        if keys.get("KeyS", False):
            move_x -= math.cos(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
            move_y -= math.sin(player.angle) * GameConfig.MOVE_SPEED * speed_mult * dt
        if keys.get("KeyA", False):
            move_x += (
                math.cos(player.angle - math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
            move_y += (
                math.sin(player.angle - math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
        if keys.get("KeyD", False):
            move_x += (
                math.cos(player.angle + math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )
            move_y += (
                math.sin(player.angle + math.pi / 2)
                * GameConfig.MOVE_SPEED
                * speed_mult
                * dt
            )

        if keys.get("ArrowLeft", False):
            player.angle -= GameConfig.ROT_SPEED * dt
        if keys.get("ArrowRight", False):
            player.angle += GameConfig.ROT_SPEED * dt

        if not self.physics.is_wall(player.x + move_x, player.y):
            player.x += move_x
        if not self.physics.is_wall(player.x, player.y + move_y):
            player.y += move_y

        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

    def update_enemies(self, dt: float):
        """Update enemy AI"""
        player = self.state.player

        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            angle_to_player = math.atan2(dy, dx)

            can_see = (
                dist < GameConfig.DETECTION_RANGE
                and self.physics.has_line_of_sight(enemy.x, enemy.y, player.x, player.y)
            )

            if enemy.state == "patrol":
                enemy.x += math.cos(enemy.patrol_dir) * GameConfig.PATROL_SPEED * dt
                enemy.y += math.sin(enemy.patrol_dir) * GameConfig.PATROL_SPEED * dt

                if self.physics.is_wall(
                    enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                    enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                ):
                    enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

                if can_see and dist < GameConfig.DETECTION_RANGE:
                    enemy.state = "chase"
                    self.log(f"Enemy spotted player at distance {dist:.2f}")

            elif enemy.state == "chase":
                if dist > GameConfig.ENEMY_ATTACK_RANGE:
                    enemy.angle = angle_to_player
                    new_x = (
                        enemy.x + math.cos(enemy.angle) * GameConfig.ENEMY_SPEED * dt
                    )
                    new_y = (
                        enemy.y + math.sin(enemy.angle) * GameConfig.ENEMY_SPEED * dt
                    )
                    if not self.physics.is_wall(new_x, enemy.y):
                        enemy.x = new_x
                    if not self.physics.is_wall(enemy.x, new_y):
                        enemy.y = new_y
                else:
                    enemy.state = "attack"

                if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
                    enemy.state = "patrol"
                    self.log("Enemy lost player, returning to patrol")

            elif enemy.state == "attack":
                if dist > GameConfig.ENEMY_ATTACK_RANGE + GameConfig.COLLISION_MARGIN:
                    enemy.state = "chase"
                elif (
                    enemy.attack_cooldown <= 0 and dist <= GameConfig.ENEMY_ATTACK_RANGE
                ):
                    enemy.attack_cooldown = GameConfig.ENEMY_ATTACK_COOLDOWN
                    player.health -= GameConfig.ENEMY_DAMAGE
                    self.log(f"Enemy attacks! Player health: {player.health}")
                    if player.health <= 0:
                        self.state.game_state = "defeat"
                        self.log("DEFEAT - Player died")

            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= dt

    def player_attack(self):
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
                self.log(f"Player hits enemy! Enemy health: {enemy.health}")

                if enemy.health <= 0:
                    enemy.state = "dying"
                    enemy.dying_progress = 0
                    self.log("Enemy entering dying state")

    def update_dying_enemies(self, dt: float):
        """Update dying enemies"""
        for enemy in self.state.enemies:
            if enemy.state == "dying":
                enemy.dying_progress += dt
                if enemy.dying_progress >= 1:
                    enemy.state = "dead"
                    self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                    self.state.kills += 1
                    self.log(f"Enemy dead. Corpses: {len(self.state.corpses)}")

    def update_hit_effects(self, dt: float):
        """Update hit effect timers"""
        for effect in self.state.hit_effects[:]:
            effect.timer -= dt
            if effect.timer <= 0:
                self.state.hit_effects.remove(effect)

    def check_conditions(self):
        """Check win/lose conditions"""
        alive_enemies = [e for e in self.state.enemies if e.state != "dead"]
        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
            self.log("VICTORY - All enemies eliminated")
