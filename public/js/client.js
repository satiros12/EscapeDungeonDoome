let ws = null;
let fps = 0;
let frameCount = 0;
let lastFpsTime = 0;

function connectWebSocket() {
    const statusEl = document.getElementById('connection-status');
    
    try {
        ws = new WebSocket(WS_URL);
        
        ws.onopen = () => {
            console.log('Connected to server');
            statusEl.textContent = 'CONECTADO';
            statusEl.classList.add('connected');
            statusEl.classList.remove('hidden');
            ws.send(JSON.stringify({ type: 'get_state' }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.game_state !== undefined) {
                    gameState = data.game_state;
                    player = data.player || player;
                    enemies = data.enemies || enemies;
                    corpses = data.corpses || corpses;
                    kills = data.kills || kills;
                    hitEffects = data.hit_effects || hitEffects;
                    
                    updateUI();
                    
                    if (paused) {
                        return;
                    }
                    
                    if (gameState === 'menu') {
                        showScreen('menu');
                    } else if (gameState === 'playing') {
                        showScreen('none');
                        document.getElementById('hud').classList.remove('hidden');
                        document.getElementById('crosshair').classList.remove('hidden');
                        document.getElementById('kill-count').classList.remove('hidden');
                        document.getElementById('fps-counter').classList.remove('hidden');
                    } else if (gameState === 'victory') {
                        showScreen('victory');
                    } else if (gameState === 'defeat') {
                        showScreen('defeat');
                    }
                }
            } catch (e) {
                console.error('Error parsing state:', e);
            }
        };
        
        ws.onclose = () => {
            console.log('Disconnected from server');
            statusEl.textContent = 'DESCONECTADO';
            statusEl.classList.remove('connected');
            setTimeout(connectWebSocket, 2000);
        };
        
        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
        };
        
    } catch (e) {
        console.error('Failed to connect:', e);
        setTimeout(connectWebSocket, 2000);
    }
}

function updateFPS(timestamp) {
    frameCount++;
    if (timestamp - lastFpsTime >= 1000) {
        fps = frameCount;
        frameCount = 0;
        lastFpsTime = timestamp;
        const fpsEl = document.getElementById('fps-counter');
        if (fpsEl) fpsEl.textContent = `FPS: ${fps}`;
    }
}

function getWebSocket() {
    return ws;
}