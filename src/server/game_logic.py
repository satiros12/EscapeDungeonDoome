"""Game logic for WebDoom server"""

import math
import random
from game_state import GameState, GameConfig, Enemy, Corpse, HitEffect, Item, EnemyType
from physics import Physics
from weapon_system import WeaponSystem


class GameLogic:
    def __init__(self, state: GameState):
        self.state = state
        self.physics = Physics(state)
        self.weapon_system = WeaponSystem(self.state)
        self.logger = None

        # Enemy type configurations
        self.enemy_configs = {
            EnemyType.IMP.value: {
                "speed": 2.5,
                "damage": 10,
                "attack_range": 1.0,
                "attack_cooldown": 1.0,
                "detection_range": 5.0,
                "patrol_speed": 1.0,
                "behavior": "chase",
            },
            EnemyType.DEMON.value: {
                "speed": 2.0,
                "damage": 15,
                "attack_range": 1.2,
                "attack_cooldown": 1.5,
                "detection_range": 6.0,
                "patrol_speed": 0.8,
                "behavior": "flanker",
            },
            EnemyType.CACODEMON.value: {
                "speed": 1.5,
                "damage": 20,
                "attack_range": 3.0,
                "attack_cooldown": 2.0,
                "detection_range": 8.0,
                "patrol_speed": 0.5,
                "behavior": "shooter",
            },
            EnemyType.SOLDIER_PISTOL.value: {
                "speed": 1.5,
                "damage": 10,
                "attack_range": 5.0,
                "attack_cooldown": 1.0,
                "detection_range": 6.0,
                "patrol_speed": 0.8,
                "behavior": "patrol",
            },
            EnemyType.SOLDIER_SHOTGUN.value: {
                "speed": 1.2,
                "damage": 20,
                "attack_range": 4.0,
                "attack_cooldown": 1.5,
                "detection_range": 5.0,
                "patrol_speed": 0.6,
                "behavior": "cover",
            },
            EnemyType.CHAINGUNNER.value: {
                "speed": 1.0,
                "damage": 15,
                "attack_range": 6.0,
                "attack_cooldown": 0.3,
                "detection_range": 7.0,
                "patrol_speed": 0.5,
                "behavior": "suppress",
            },
        }

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
        self.collect_items()
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

        if not self.physics.check_collision(player.x + move_x, player.y):
            player.x += move_x
        if not self.physics.check_collision(player.x, player.y + move_y):
            player.y += move_y

        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

    def update_enemies(self, dt: float):
        """Update enemy AI with different behaviors per enemy type"""
        player = self.state.player

        alive_enemies = [
            e for e in self.state.enemies if e.state not in ("dead", "dying")
        ]

        for enemy in alive_enemies:
            # Get enemy configuration based on type
            enemy_type = enemy.enemy_type
            config = self.enemy_configs.get(enemy_type, self.enemy_configs["imp"])

            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            angle_to_player = math.atan2(dy, dx)

            # Use enemy-specific detection range
            detection_range = config.get("detection_range", GameConfig.DETECTION_RANGE)
            can_see = dist < detection_range and self.physics.has_line_of_sight(
                enemy.x, enemy.y, player.x, player.y
            )

            behavior = config.get("behavior", "chase")

            # Handle different behaviors
            if behavior == "chase":
                self._update_imp_behavior(
                    enemy, player, dt, dist, angle_to_player, can_see, config
                )
            elif behavior == "flanker":
                self._update_demon_behavior(
                    enemy, player, dt, dist, angle_to_player, can_see, config
                )
            elif behavior == "shooter":
                self._update_cacodemon_behavior(
                    enemy, player, dt, dist, angle_to_player, can_see, config
                )
            elif behavior in ("patrol", "cover", "suppress"):
                self._update_soldier_behavior(
                    enemy, player, dt, dist, angle_to_player, can_see, config
                )
            else:
                # Default behavior
                self._update_imp_behavior(
                    enemy, player, dt, dist, angle_to_player, can_see, config
                )

            # Update attack cooldown
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= dt

    def _update_imp_behavior(
        self, enemy, player, dt, dist, angle_to_player, can_see, config
    ):
        """Imp behavior: direct chase"""
        patrol_speed = config.get("patrol_speed", 1.0)
        detection_range = config.get("detection_range", 5.0)

        if enemy.state == "patrol":
            enemy.x += math.cos(enemy.patrol_dir) * patrol_speed * dt
            enemy.y += math.sin(enemy.patrol_dir) * patrol_speed * dt

            if self.physics.is_wall(
                enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
            ):
                enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

            if can_see and dist < detection_range:
                enemy.state = "chase"
                self.log(f"Imp spotted player at distance {dist:.2f}")

        elif enemy.state == "chase":
            speed = config.get("speed", 2.5)
            attack_range = config.get("attack_range", 1.0)

            if dist > attack_range:
                enemy.angle = angle_to_player
                new_x = enemy.x + math.cos(enemy.angle) * speed * dt
                new_y = enemy.y + math.sin(enemy.angle) * speed * dt
                if not self.physics.is_wall(new_x, enemy.y):
                    enemy.x = new_x
                if not self.physics.is_wall(enemy.x, new_y):
                    enemy.y = new_y
            else:
                enemy.state = "attack"

            if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
                enemy.state = "patrol"
                self.log("Imp lost player, returning to patrol")

        elif enemy.state == "attack":
            attack_range = config.get("attack_range", 1.0)
            cooldown = config.get("attack_cooldown", 1.0)
            damage = config.get("damage", 10)

            if dist > attack_range + GameConfig.COLLISION_MARGIN:
                enemy.state = "chase"
            elif enemy.attack_cooldown <= 0 and dist <= attack_range:
                enemy.attack_cooldown = cooldown
                actual_damage, armor_damage = self.apply_armor_reduction(damage)
                player.health -= actual_damage
                self.log(
                    f"Imp attacks! Damage: {actual_damage}, Armor absorbed: {armor_damage}. Player health: {player.health}"
                )
                if player.health <= 0:
                    self.state.game_state = "defeat"
                    self.log("DEFEAT - Player died")

    def _update_demon_behavior(
        self, enemy, player, dt, dist, angle_to_player, can_see, config
    ):
        """Demon behavior: flanker - moves to sides"""
        patrol_speed = config.get("patrol_speed", 0.8)
        detection_range = config.get("detection_range", 6.0)

        if enemy.state == "patrol":
            enemy.x += math.cos(enemy.patrol_dir) * patrol_speed * dt
            enemy.y += math.sin(enemy.patrol_dir) * patrol_speed * dt

            if self.physics.is_wall(
                enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
            ):
                enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

            if can_see and dist < detection_range:
                enemy.state = "chase"
                # Start at angle to flank
                enemy.patrol_dir = angle_to_player + (
                    math.pi / 4 if random.random() > 0.5 else -math.pi / 4
                )
                self.log(f"Demon spotted player, flanking at distance {dist:.2f}")

        elif enemy.state == "chase":
            speed = config.get("speed", 2.0)
            attack_range = config.get("attack_range", 1.2)

            if dist > attack_range:
                enemy.angle = angle_to_player
                # Flank: move at an angle to the player
                flank_angle = angle_to_player + (
                    math.pi / 4 if random.random() > 0.5 else -math.pi / 4
                )
                new_x = enemy.x + math.cos(flank_angle) * speed * dt
                new_y = enemy.y + math.sin(flank_angle) * speed * dt
                if not self.physics.is_wall(new_x, enemy.y):
                    enemy.x = new_x
                if not self.physics.is_wall(enemy.x, new_y):
                    enemy.y = new_y
            else:
                enemy.state = "attack"

            if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
                enemy.state = "patrol"
                self.log("Demon lost player, returning to patrol")

        elif enemy.state == "attack":
            attack_range = config.get("attack_range", 1.2)
            cooldown = config.get("attack_cooldown", 1.5)
            damage = config.get("damage", 15)

            if dist > attack_range + GameConfig.COLLISION_MARGIN:
                enemy.state = "chase"
            elif enemy.attack_cooldown <= 0 and dist <= attack_range:
                enemy.attack_cooldown = cooldown
                actual_damage, armor_damage = self.apply_armor_reduction(damage)
                player.health -= actual_damage
                self.log(
                    f"Demon attacks! Damage: {actual_damage}, Armor absorbed: {armor_damage}. Player health: {player.health}"
                )
                if player.health <= 0:
                    self.state.game_state = "defeat"
                    self.log("DEFEAT - Player died")

    def _update_cacodemon_behavior(
        self, enemy, player, dt, dist, angle_to_player, can_see, config
    ):
        """Cacodemon behavior: shooter - maintains distance"""
        patrol_speed = config.get("patrol_speed", 0.5)
        detection_range = config.get("detection_range", 8.0)

        if enemy.state == "patrol":
            enemy.x += math.cos(enemy.patrol_dir) * patrol_speed * dt
            enemy.y += math.sin(enemy.patrol_dir) * patrol_speed * dt

            if self.physics.is_wall(
                enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
            ):
                enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

            if can_see and dist < detection_range:
                enemy.state = "chase"
                self.log(f"Cacodemon spotted player at distance {dist:.2f}")

        elif enemy.state == "chase":
            speed = config.get("speed", 1.5)
            attack_range = config.get("attack_range", 3.0)

            # Maintain distance (2-3 units away)
            if dist > attack_range + 1.0:
                enemy.angle = angle_to_player
                new_x = enemy.x + math.cos(enemy.angle) * speed * dt
                new_y = enemy.y + math.sin(enemy.angle) * speed * dt
                if not self.physics.is_wall(new_x, enemy.y):
                    enemy.x = new_x
                if not self.physics.is_wall(enemy.x, new_y):
                    enemy.y = new_y
            elif dist < 2.0:
                # Back away
                enemy.angle = angle_to_player + math.pi
                new_x = enemy.x + math.cos(enemy.angle) * speed * 0.5 * dt
                new_y = enemy.y + math.sin(enemy.angle) * speed * 0.5 * dt
                if not self.physics.is_wall(new_x, enemy.y):
                    enemy.x = new_x
                if not self.physics.is_wall(enemy.x, new_y):
                    enemy.y = new_y
            else:
                enemy.state = "attack"

            if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
                enemy.state = "patrol"
                self.log("Cacodemon lost player, returning to patrol")

        elif enemy.state == "attack":
            attack_range = config.get("attack_range", 3.0)
            cooldown = config.get("attack_cooldown", 2.0)
            damage = config.get("damage", 20)

            if dist > attack_range + GameConfig.COLLISION_MARGIN:
                enemy.state = "chase"
            elif enemy.attack_cooldown <= 0 and dist <= attack_range:
                enemy.attack_cooldown = cooldown
                actual_damage, armor_damage = self.apply_armor_reduction(damage)
                player.health -= actual_damage
                self.log(
                    f"Cacodemon attacks! Damage: {actual_damage}, Armor absorbed: {armor_damage}. Player health: {player.health}"
                )
                if player.health <= 0:
                    self.state.game_state = "defeat"
                    self.log("DEFEAT - Player died")

    def _update_soldier_behavior(
        self, enemy, player, dt, dist, angle_to_player, can_see, config
    ):
        """Soldier behavior: uses weapon, maintains cover"""
        patrol_speed = config.get("patrol_speed", 0.8)
        detection_range = config.get("detection_range", 6.0)
        attack_range = config.get("attack_range", 5.0)
        weapon = enemy.weapon

        if enemy.state == "patrol":
            enemy.x += math.cos(enemy.patrol_dir) * patrol_speed * dt
            enemy.y += math.sin(enemy.patrol_dir) * patrol_speed * dt

            if self.physics.is_wall(
                enemy.x + math.cos(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
                enemy.y + math.sin(enemy.patrol_dir) * GameConfig.COLLISION_MARGIN,
            ):
                enemy.patrol_dir += math.pi / 2 + random.random() * math.pi

            if can_see and dist < detection_range:
                enemy.state = "chase"
                self.log(f"Soldier ({weapon}) spotted player at distance {dist:.2f}")

        elif enemy.state == "chase":
            speed = config.get("speed", 1.5)

            # Stop at attack range
            if dist > attack_range:
                enemy.angle = angle_to_player
                new_x = enemy.x + math.cos(enemy.angle) * speed * dt
                new_y = enemy.y + math.sin(enemy.angle) * speed * dt
                if not self.physics.is_wall(new_x, enemy.y):
                    enemy.x = new_x
                if not self.physics.is_wall(enemy.x, new_y):
                    enemy.y = new_y
            else:
                enemy.state = "attack"

            if not can_see and dist > GameConfig.LOST_PLAYER_DISTANCE:
                enemy.state = "patrol"
                self.log("Soldier lost player, returning to patrol")

        elif enemy.state == "attack":
            cooldown = config.get("attack_cooldown", 1.0)
            damage = config.get("damage", 10)

            if dist > attack_range + GameConfig.COLLISION_MARGIN:
                enemy.state = "chase"
            elif enemy.attack_cooldown <= 0 and dist <= attack_range:
                enemy.attack_cooldown = cooldown
                enemy.angle = angle_to_player

                # Soldiers use their weapon - deal damage
                actual_damage, armor_damage = self.apply_armor_reduction(damage)
                player.health -= actual_damage
                self.log(
                    f"Soldier ({weapon}) attacks! Damage: {actual_damage}, Armor absorbed: {armor_damage}. Player health: {player.health}"
                )
                if player.health <= 0:
                    self.state.game_state = "defeat"
                    self.log("DEFEAT - Player died")

    def player_attack(self):
        """Player attacks using current weapon"""
        result = self.weapon_system.player_attack()

        if result.get("success"):
            # Add hit effects for each hit
            for hit in result.get("hits", []):
                self.state.hit_effects.append(HitEffect(x=hit["x"], y=hit["y"]))
                self.log(
                    f"Player hits enemy with {result['weapon']}! Damage: {hit['damage']}"
                )

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
        # Check goal reached
        if self.state.goal and not self.state.goal_reached:
            player = self.state.player
            goal_x, goal_y = self.state.goal
            dist = math.sqrt((player.x - goal_x) ** 2 + (player.y - goal_y) ** 2)
            if dist < 1.0:
                self.state.goal_reached = True
                self.state.game_state = "victory"
                self.log("VICTORY - Goal reached!")
                return

        # Check all enemies defeated (original condition)
        alive_enemies = [e for e in self.state.enemies if e.state != "dead"]
        if len(alive_enemies) == 0 and self.state.game_state == "playing":
            self.state.game_state = "victory"
            self.log("VICTORY - All enemies eliminated")

    def collect_items(self):
        """Check and collect items near player"""
        player = self.state.player

        for item in self.state.items:
            if item.collected:
                continue

            dist = math.sqrt((player.x - item.x) ** 2 + (player.y - item.y) ** 2)
            if dist < 1.0:
                self._collect_item(item)

    def _collect_item(self, item: Item):
        """Collect a specific item"""
        player = self.state.player

        if item.item_type == "health_pack":
            heal_amount = item.value if item.value > 0 else 25
            player.health = min(
                GameConfig.PLAYER_MAX_HEALTH, player.health + heal_amount
            )
            self.log(f"Collected health pack! Health: {player.health}")

        elif item.item_type == "ammo_shotgun":
            ammo_amount = item.value if item.value > 0 else 10
            player.ammo["shotgun"] = player.ammo.get("shotgun", 0) + ammo_amount
            self.log(f"Collected shotgun ammo! Shotgun: {player.ammo['shotgun']}")

        elif item.item_type == "ammo_chaingun":
            ammo_amount = item.value if item.value > 0 else 50
            player.ammo["chaingun"] = player.ammo.get("chaingun", 0) + ammo_amount
            self.log(f"Collected chaingun ammo! Chaingun: {player.ammo['chaingun']}")

        elif item.item_type == "armor_light":
            armor_amount = item.value if item.value > 0 else 25
            player.armor = min(100, player.armor + armor_amount)
            player.armor_type = "light"
            self.log(f"Collected light armor! Armor: {player.armor}")

        elif item.item_type == "armor_heavy":
            armor_amount = item.value if item.value > 0 else 50
            player.armor = min(100, player.armor + armor_amount)
            player.armor_type = "heavy"
            self.log(f"Collected heavy armor! Armor: {player.armor}")

        elif item.item_type in ("weapon_fists", "weapon_sword", "weapon_axe"):
            self.log(f"Collected weapon: {item.item_type}")

        item.collected = True

    def apply_armor_reduction(self, damage: int) -> tuple:
        """Apply armor damage reduction. Returns (actual_damage, armor_damage)"""
        player = self.state.player

        if player.armor <= 0:
            return damage, 0

        armor_protection = 0.5 if player.armor_type == "light" else 0.75

        actual_damage = int(damage * (1 - armor_protection))
        armor_damage = int(damage * armor_protection)

        player.armor = max(0, player.armor - armor_damage)

        if player.armor <= 0:
            player.armor_type = "none"

        return actual_damage, armor_damage
