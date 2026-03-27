/** Raycaster - Raycasting engine for pseudo-3D rendering */

class Raycaster {
    constructor(config = {}) {
        this.FOV = config.FOV || Math.PI / 3;
        this.HALF_FOV = this.FOV / 2;
        this.NUM_RAYS = config.NUM_RAYS || 320;
        this.MAX_DEPTH = config.MAX_DEPTH || 16;
        this.RAY_STEP = config.RAY_STEP || 0.02;
    }

    castRays(playerX, playerY, playerAngle, isWallFn) {
        const rays = [];
        
        for (let i = 0; i < this.NUM_RAYS; i++) {
            const rayAngle = playerAngle - this.HALF_FOV + (i / this.NUM_RAYS) * this.FOV;
            const ray = this.castSingleRay(playerX, playerY, rayAngle, isWallFn);
            rays.push(ray);
        }
        
        return rays;
    }

    castSingleRay(rayAngle, playerX, playerY, isWallFn) {
        const sinVal = Math.sin(rayAngle);
        const cosVal = Math.cos(rayAngle);
        
        const safeSin = Math.abs(sinVal) < 0.0001 ? 0.0001 * Math.sign(sinVal || 1) : sinVal;
        const safeCos = Math.abs(cosVal) < 0.0001 ? 0.0001 * Math.sign(cosVal || 1) : cosVal;
        
        let dist = 0;
        let hitX, hitY;
        let side = 0;
        
        while (dist < this.MAX_DEPTH) {
            dist += this.RAY_STEP;
            hitX = playerX + safeCos * dist;
            hitY = playerY + safeSin * dist;
            
            if (isWallFn(hitX, hitY)) {
                const prevX = playerX + safeCos * (dist - this.RAY_STEP);
                const prevY = playerY + safeSin * (dist - this.RAY_STEP);
                side = Math.floor(hitX) !== Math.floor(prevX) ? 1 : 0;
                
                return {
                    dist: dist,
                    side: side,
                    x: hitX,
                    y: hitY
                };
            }
        }
        
        return {
            dist: this.MAX_DEPTH,
            side: 0,
            x: playerX + safeCos * this.MAX_DEPTH,
            y: playerY + safeSin * this.MAX_DEPTH
        };
    }

    getProjectionDistance(rayDist, rayAngle, playerAngle) {
        const diffAngle = rayAngle - playerAngle;
        return rayDist * Math.cos(diffAngle);
    }
}


class WallRenderer {
    constructor(canvas, config = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        
        this.wallColorBase = config.wallColorBase || [255, 200, 180];
        this.wallColorSide = config.wallColorSide || [180, 160, 140];
        this.minBrightness = config.minBrightness || 0.3;
        
        this.raycaster = new Raycaster(config);
    }

    render(gameState, mapData) {
        const { player, enemies, corpses } = gameState;
        if (!player) return;
        
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this._renderCeilingFloor();
        
        const isWall = (x, y) => this._isWall(x, y, mapData);
        const rays = this.raycaster.castRays(player.x, player.y, player.angle, isWall);
        
        this._renderWalls(rays, player.angle);
        
        this._renderSprites(gameState, mapData);
    }

    _renderCeilingFloor() {
        const halfHeight = this.height / 2;
        
        this.ctx.fillStyle = '#1a1a2e';
        this.ctx.fillRect(0, 0, this.width, halfHeight);
        
        this.ctx.fillStyle = '#2d2d2d';
        this.ctx.fillRect(0, halfHeight, this.width, halfHeight);
    }

    _renderWalls(rays, playerAngle) {
        const stripWidth = this.width / rays.length;
        
        for (let i = 0; i < rays.length; i++) {
            const ray = rays[i];
            const correctedDist = this.raycaster.getProjectionDistance(
                ray.dist, 
                playerAngle - this.raycaster.HALF_FOV + (i / rays.length) * this.raycaster.FOV,
                0
            );
            
            if (correctedDist <= 0) continue;
            
            const wallHeight = (this.height / correctedDist);
            const wallTop = (this.height - wallHeight) / 2;
            
            let brightness = Math.min(1, this.raycaster.MAX_DEPTH / correctedDist);
            brightness = Math.max(brightness, this.minBrightness);
            
            const color = ray.side === 0 ? this.wallColorBase : this.wallColorSide;
            const r = Math.floor(color[0] * brightness);
            const g = Math.floor(color[1] * brightness);
            const b = Math.floor(color[2] * brightness);
            
            this.ctx.fillStyle = `rgb(${r},${g},${b})`;
            this.ctx.fillRect(
                Math.floor(i * stripWidth),
                Math.floor(wallTop),
                Math.ceil(stripWidth),
                Math.ceil(wallHeight)
            );
        }
    }

    _renderSprites(gameState, mapData) {
        const { player, enemies, corpses } = gameState;
        if (!player) return;
        
        const sprites = [
            ...(enemies || []).filter(e => e.state !== 'dead').map(e => ({...e, type: 'enemy'})),
            ...(corpses || []).map(c => ({...c, type: 'corpse'}))
        ];
        
        const sortedSprites = sprites
            .map(sprite => ({
                ...sprite,
                distance: Math.sqrt(
                    Math.pow(sprite.x - player.x, 2) + 
                    Math.pow(sprite.y - player.y, 2)
                )
            }))
            .sort((a, b) => b.distance - a.distance);
        
        for (const sprite of sortedSprites) {
            this._renderSprite(sprite, player);
        }
    }

    _renderSprite(sprite, player) {
        const dx = sprite.x - player.x;
        const dy = sprite.y - player.y;
        
        let angle = Math.atan2(dy, dx) - player.angle;
        while (angle > Math.PI) angle -= 2 * Math.PI;
        while (angle < -Math.PI) angle += 2 * Math.PI;
        
        const distance = sprite.distance;
        
        if (Math.abs(angle) > this.raycaster.HALF_FOV + 0.2) return;
        if (distance < 0.3) return;
        
        const spriteHeight = this.height / distance;
        const spriteWidth = spriteHeight * 0.8;
        
        const screenX = this.width / 2 + (angle / this.raycaster.HALF_FOV) * (this.width / 2);
        const screenY = (this.height - spriteHeight) / 2;
        
        const brightness = Math.min(1, this.raycaster.MAX_DEPTH / distance);
        
        this.ctx.globalAlpha = brightness;
        
        if (sprite.type === 'enemy') {
            this._drawEnemy(sprite, screenX, screenY, spriteWidth, spriteHeight, sprite.state);
        } else if (sprite.type === 'corpse') {
            this._drawCorpse(screenX, screenY, spriteWidth, spriteHeight);
        }
        
        this.ctx.globalAlpha = 1;
    }

    _drawEnemy(x, y, w, h, state) {
        const hue = state === 'dying' ? 0 : 0;
        const sat = state === 'dying' ? 100 : 80;
        const lig = state === 'dying' ? 50 : 60;
        
        this.ctx.fillStyle = `hsl(${hue}, ${sat}%, ${lig}%)`;
        
        this.ctx.beginPath();
        this.ctx.arc(x + w/2, y + h/2, w/2, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.fillStyle = '#ff0';
        this.ctx.beginPath();
        this.ctx.arc(x + w*0.35, y + h*0.35, w*0.1, 0, Math.PI * 2);
        this.ctx.arc(x + w*0.65, y + h*0.35, w*0.1, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.fillStyle = '#f00';
        this.ctx.beginPath();
        this.ctx.arc(x + w*0.5, y + h*0.7, w*0.15, 0, Math.PI);
        this.ctx.fill();
    }

    _drawCorpse(x, y, w, h) {
        this.ctx.fillStyle = '#4a1a1a';
        this.ctx.beginPath();
        this.ctx.ellipse(x + w/2, y + h/2, w/2, h/3, 0, 0, Math.PI * 2);
        this.ctx.fill();
    }

    _isWall(x, y, mapData) {
        const mx = Math.floor(x);
        const my = Math.floor(y);
        
        if (my < 0 || my >= mapData.length) return true;
        if (mx < 0 || mx >= mapData[0].length) return true;
        
        return mapData[my][mx] === '#';
    }

    resize(width, height) {
        this.width = width;
        this.height = height;
    }
}
