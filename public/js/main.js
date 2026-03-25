let player = { x: 1.5, y: 1.5, angle: 0, health: 100, attack_cooldown: 0 };
let enemies = [];
let corpses = [];
let kills = 0;
let hitEffects = [];

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

showScreen('menu');
connectWebSocket();
requestAnimationFrame(render);