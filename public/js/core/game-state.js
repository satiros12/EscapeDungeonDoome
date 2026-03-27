class GameState extends Observable {
    constructor() {
        super();
        this.gameState = 'menu';
        this.player = { x: 1.5, y: 1.5, angle: 0, health: 100, attack_cooldown: 0 };
        this.enemies = [];
        this.corpses = [];
        this.kills = 0;
        this.hitEffects = [];
    }

    updateFromServer(data) {
        const prevHealth = this.player?.health;
        
        if (data.game_state !== undefined) {
            this.gameState = data.game_state;
        }
        if (data.player) {
            this.player = { ...this.player, ...data.player };
        }
        if (data.enemies) {
            this.enemies = data.enemies;
        }
        if (data.corpses) {
            this.corpses = data.corpses;
        }
        if (data.kills !== undefined) {
            this.kills = data.kills;
        }
        if (data.hit_effects) {
            this.hitEffects = data.hit_effects;
        }

        this.notify({
            type: 'state_updated',
            data,
            playerHealthChanged: this.player.health !== prevHealth,
            playerTookDamage: this.player.health < prevHealth
        });
    }

    getGameState() {
        return this.gameState;
    }

    getPlayer() {
        return this.player;
    }

    getEnemies() {
        return this.enemies;
    }

    getCorpses() {
        return this.corpses;
    }

    reset() {
        this.gameState = 'menu';
        this.player = { x: 1.5, y: 1.5, angle: 0, health: 100, attack_cooldown: 0 };
        this.enemies = [];
        this.corpses = [];
        this.kills = 0;
        this.hitEffects = [];
        this.notify({ type: 'reset' });
    }
}
