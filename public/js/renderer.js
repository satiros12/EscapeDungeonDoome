let SCREEN_WIDTH = window.innerWidth;
let SCREEN_HEIGHT = window.innerHeight;
const FOV = CONFIG.FOV;
const HALF_FOV = CONFIG.HALF_FOV;
const NUM_RAYS = CONFIG.NUM_RAYS;
const MAX_DEPTH = CONFIG.MAX_DEPTH;

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

if (!ctx) {
    document.body.innerHTML = '<h1 style="color:red;text-align:center;margin-top:20%;font-family:sans-serif;">Error: Canvas 2D not supported</h1>';
    throw new Error('Canvas 2D context not available');
}

function resizeCanvas() {
    SCREEN_WIDTH = window.innerWidth;
    SCREEN_HEIGHT = window.innerHeight;
    canvas.width = SCREEN_WIDTH;
    canvas.height = SCREEN_HEIGHT;
}

function isWall(x, y) {
    const mx = Math.floor(x);
    const my = Math.floor(y);
    if (mx < 0 || mx >= MAP_WIDTH || my < 0 || my >= MAP_HEIGHT) return true;
    return mapData[my][mx] === '#';
}

function castRay(rayAngle) {
    let sin = Math.sin(rayAngle);
    let cos = Math.cos(rayAngle);
    if (Math.abs(sin) < 0.0001) sin = 0.0001;
    if (Math.abs(cos) < 0.0001) cos = 0.0001;

    let dist = 0;
    const step = CONFIG.RAY_STEP;
    while (dist < MAX_DEPTH) {
        dist += step;
        const testX = player.x + cos * dist;
        const testY = player.y + sin * dist;
        if (isWall(testX, testY)) {
            let side = 0;
            const mx = Math.floor(testX);
            const my = Math.floor(testY);
            if (mx !== Math.floor(player.x + cos * (dist - step))) side = 1;
            return { dist, side };
        }
    }
    return { dist: MAX_DEPTH, side: 0 };
}

function renderWalls() {
    const stripWidth = SCREEN_WIDTH / NUM_RAYS;
    for (let i = 0; i < NUM_RAYS; i++) {
        const rayAngle = player.angle - HALF_FOV + (i / NUM_RAYS) * FOV;
        const { dist, side } = castRay(rayAngle);
        const correctedDist = dist * Math.cos(rayAngle - player.angle);
        const wallHeight = Math.min(SCREEN_HEIGHT * 2, SCREEN_HEIGHT / correctedDist);
        const brightness = Math.max(CONFIG.MIN_BRIGHTNESS, 1 - correctedDist / MAX_DEPTH);
        const color = side === 0 
            ? [brightness * CONFIG.WALL_COLOR_BASE[0], brightness * CONFIG.WALL_COLOR_BASE[1], brightness * CONFIG.WALL_COLOR_BASE[2]] 
            : [brightness * CONFIG.WALL_COLOR_SIDE[0], brightness * CONFIG.WALL_COLOR_SIDE[1], brightness * CONFIG.WALL_COLOR_SIDE[2]];
        ctx.fillStyle = `rgb(${color[0]},${color[1]},${color[2]})`;
        ctx.fillRect(i * stripWidth, (SCREEN_HEIGHT - wallHeight) / 2, stripWidth + 1, wallHeight);
    }
}

function renderFloor() {
    const gradient = ctx.createLinearGradient(0, SCREEN_HEIGHT / 2, 0, SCREEN_HEIGHT);
    gradient.addColorStop(0, '#1a1a1a');
    gradient.addColorStop(1, '#0a0a0a');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT / 2);
}

function renderCeiling() {
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2);
}

function normalizeAngle(angle) {
    while (angle > Math.PI) angle -= Math.PI * 2;
    while (angle < -Math.PI) angle += Math.PI * 2;
    return angle;
}

function renderSprites() {
    const sprites = [];

    enemies.forEach(enemy => {
        if (enemy.state === 'dead') return;
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const angleToEnemy = Math.atan2(dy, dx);
        let angleDiff = normalizeAngle(angleToEnemy - player.angle);
        if (Math.abs(angleDiff) < HALF_FOV + CONFIG.FOV_CULL && dist < MAX_DEPTH) {
            sprites.push({ ...enemy, dist, angleDiff, isEnemy: true });
        }
    });

    corpses.forEach(corpse => {
        const dx = corpse.x - player.x;
        const dy = corpse.y - player.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const angleToCorpse = Math.atan2(dy, dx);
        const angleDiff = normalizeAngle(angleToCorpse - player.angle);
        if (Math.abs(angleDiff) < HALF_FOV + CONFIG.FOV_CULL && dist < MAX_DEPTH) {
            sprites.push({ x: corpse.x, y: corpse.y, dist, angleDiff, isEnemy: false, isCorpse: true });
        }
    });

    sprites.sort((a, b) => b.dist - a.dist);

    sprites.forEach(sprite => {
        const screenX = SCREEN_WIDTH / 2 + (sprite.angleDiff / HALF_FOV) * (SCREEN_WIDTH / 2);
        const size = Math.min(400, SCREEN_HEIGHT / sprite.dist * 0.6);
        const screenY = SCREEN_HEIGHT / 2;

        if (sprite.isCorpse) {
            ctx.fillStyle = '#440000';
            ctx.beginPath();
            ctx.arc(screenX, screenY + size * 0.3, size / 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#220000';
            ctx.fillRect(screenX - size / 2, screenY, size, size / 4);
        } else if (sprite.state === 'dying') {
            const alpha = 1 - sprite.dying_progress;
            ctx.fillStyle = `rgba(102, 0, 0, ${alpha})`;
            ctx.beginPath();
            ctx.arc(screenX, screenY, size / 2 * (1 + sprite.dying_progress * 0.3), 0, Math.PI * 2);
            ctx.fill();
        } else {
            const color = sprite.state === 'chase' || sprite.state === 'attack' ? '#ff2222' : '#aa3333';
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(screenX, screenY, size / 2, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(screenX - size / 6, screenY - size / 6, size / 10, 0, Math.PI * 2);
            ctx.fill();

            if (sprite.state === 'attack') {
                ctx.fillStyle = '#ff0000';
                ctx.beginPath();
                ctx.moveTo(screenX + size / 2, screenY);
                ctx.lineTo(screenX + size / 2 + 20, screenY - 10);
                ctx.lineTo(screenX + size / 2 + 20, screenY + 10);
                ctx.fill();
            }
        }
    });
}

function renderHitEffects() {
    hitEffects.forEach(effect => {
        const dx = effect.x - player.x;
        const dy = effect.y - player.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const angleToEffect = Math.atan2(dy, dx);
        const angleDiff = normalizeAngle(angleToEffect - player.angle);
        if (Math.abs(angleDiff) < HALF_FOV + CONFIG.FOV_CULL && dist < MAX_DEPTH) {
            const screenX = SCREEN_WIDTH / 2 + (angleDiff / HALF_FOV) * (SCREEN_WIDTH / 2);
            const size = Math.min(100, SCREEN_HEIGHT / dist * 0.15);
            const screenY = SCREEN_HEIGHT / 2;
            const alpha = effect.timer / 0.3;
            ctx.strokeStyle = `rgba(255, 255, 0, ${alpha})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(screenX, screenY, size, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillStyle = `rgba(255, 255, 0, ${alpha})`;
            ctx.font = `${size}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText('HIT!', screenX, screenY - size - 5);
        }
    });
}

function render(timestamp) {
    updateFPS(timestamp);
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    renderCeiling();
    renderFloor();
    renderWalls();
    renderSprites();
    renderHitEffects();
    updateHUD();
    requestAnimationFrame(render);
}