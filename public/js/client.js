let ws = null;
let fps = 0;
let frameCount = 0;
let lastFpsTime = 0;
let currentMapName = 'Base Map';

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
            ws.send(JSON.stringify({ type: 'get_maps' }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'maps_list' || data.type === 'map_changed' || data.type === 'map_selected') {
                    updateMapSelector(data);
                    return;
                }
                
                if (data.type === 'weapon_changed') {
                    // Update weapon info from server response
                    if (data.weapon && player) {
                        player.current_weapon = data.weapon;
                    }
                    if (data.ammo && player) {
                        player.ammo = data.ammo;
                    }
                    updateHUD();
                    return;
                }
                
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

function updateMapSelector(data) {
    const nameEl = document.getElementById('map-name');
    const descEl = document.getElementById('map-desc');
    
    const mapName = data.map_name || data.current_map_name || 'Unknown';
    currentMapName = mapName;
    
    if (nameEl) {
        nameEl.textContent = mapName;
    }
    
    if (descEl) {
        const descriptions = {
            'Base Map': 'Classic corridors',
            'Arena': 'Open combat arena',
            'Maze': 'Complex maze layout',
            'Arena 2': 'Large arena with pillars'
        };
        descEl.textContent = descriptions[mapName] || '';
    }
}

function selectPrevMap() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'prev_map' }));
    }
}

function selectNextMap() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'next_map' }));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const prevBtn = document.getElementById('prevMap');
    const nextBtn = document.getElementById('nextMap');
    if (prevBtn) {
        prevBtn.addEventListener('click', selectPrevMap);
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', selectNextMap);
    }
});