/** Game Facade - Main client entry point */

class Game {
    constructor() {
        this.state = new GameState();
        this.ws = null;
        this.paused = false;
        this.consoleOpen = false;
        this.keys = {};
        
        this._setupEventListeners();
        this._connect();
        this._startRenderLoop();
    }

    _setupEventListeners() {
        this.state.subscribe({
            onEvent: (event) => {
                if (event.type === 'state_updated') {
                    if (event.playerTookDamage) {
                        this._showDamageFlash();
                    }
                }
            }
        });

        document.addEventListener('keydown', (e) => this._handleKeyDown(e));
        document.addEventListener('keyup', (e) => this._handleKeyUp(e));

        document.getElementById('startBtn')?.addEventListener('click', () => this.start());
        document.getElementById('victoryBtn')?.addEventListener('click', () => this.returnToMenu());
        document.getElementById('defeatBtn')?.addEventListener('click', () => this.returnToMenu());
        document.getElementById('resumeBtn')?.addEventListener('click', () => this.resume());
        document.getElementById('pauseMenuBtn')?.addEventListener('click', () => this.returnToMenu());
        
        document.getElementById('prevMap')?.addEventListener('click', () => this._selectPrevMap());
        document.getElementById('nextMap')?.addEventListener('click', () => this._selectNextMap());
        
        // Controles tactiles - asegurar que no propagan eventos
        this._setupTouchControls();
        
        this._requestMapsList();
    }
    
    _setupTouchControls() {
        const touchControls = document.getElementById('touch-controls');
        if (touchControls) {
            touchControls.addEventListener('touchstart', (e) => e.stopPropagation(), { passive: true });
            touchControls.addEventListener('touchmove', (e) => e.stopPropagation(), { passive: true });
            touchControls.addEventListener('touchend', (e) => e.stopPropagation(), { passive: true });
        }
        
        const joystick = document.getElementById('touch-joystick');
        if (joystick) {
            joystick.addEventListener('touchstart', (e) => e.stopPropagation(), { passive: true });
            joystick.addEventListener('touchmove', (e) => e.stopPropagation(), { passive: true });
            joystick.addEventListener('touchend', (e) => e.stopPropagation(), { passive: true });
        }
        
        const buttons = document.getElementById('touch-buttons');
        if (buttons) {
            buttons.addEventListener('touchstart', (e) => e.stopPropagation(), { passive: true });
            buttons.addEventListener('touchend', (e) => e.stopPropagation(), { passive: true });
        }
        
        // Botones tactiles - conectar con metodos del juego
        const btnAttack = document.getElementById('btn-attack');
        const btnPause = document.getElementById('btn-pause');
        const btnRotateLeft = document.getElementById('btn-rotate-left');
        const btnRotateRight = document.getElementById('btn-rotate-right');
        
        if (btnAttack) {
            btnAttack.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this.keys['Space'] = true;
                    this._sendInput();
                    this._sendAttack();
                    setTimeout(() => {
                        this.keys['Space'] = false;
                        this._sendInput();
                    }, 100);
                }
            }, { passive: false });
        }
        
        if (btnPause) {
            btnPause.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this.pause();
                }
            }, { passive: false });
        }
        
        if (btnRotateLeft) {
            btnRotateLeft.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this.keys['ArrowLeft'] = true;
                    this._sendInput();
                }
            }, { passive: false });
            btnRotateLeft.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.keys['ArrowLeft'] = false;
                this._sendInput();
            }, { passive: false });
        }
        
        if (btnRotateRight) {
            btnRotateRight.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this.keys['ArrowRight'] = true;
                    this._sendInput();
                }
            }, { passive: false });
            btnRotateRight.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.keys['ArrowRight'] = false;
                this._sendInput();
            }, { passive: false });
        }
        
        // Botones tactiles de cambio de arma
        const btnWeapon1 = document.getElementById('btn-weapon-1');
        const btnWeapon2 = document.getElementById('btn-weapon-2');
        const btnWeapon3 = document.getElementById('btn-weapon-3');
        
        if (btnWeapon1) {
            btnWeapon1.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this._sendWeaponChange('fists');
                }
            }, { passive: false });
        }
        
        if (btnWeapon2) {
            btnWeapon2.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this._sendWeaponChange('sword');
                }
            }, { passive: false });
        }
        
        if (btnWeapon3) {
            btnWeapon3.addEventListener('touchstart', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
                    this._sendWeaponChange('axe');
                }
            }, { passive: false });
        }
    }
    
    _requestMapsList() {
        this._send({ type: 'get_maps' });
    }
    
    _selectPrevMap() {
        this._send({ type: 'prev_map' });
    }
    
    _selectNextMap() {
        this._send({ type: 'next_map' });
    }
    
    _updateMapSelector(data) {
        const nameEl = document.getElementById('map-name');
        const descEl = document.getElementById('map-desc');
        
        if (nameEl && data.map_name) {
            nameEl.textContent = data.map_name;
        }
        
        if (descEl) {
            const descriptions = {
                'Base Map': 'Classic corridors',
                'Arena': 'Open combat arena',
                'Maze': 'Complex maze layout',
                'Arena 2': 'Large arena with pillars'
            };
            descEl.textContent = descriptions[data.map_name] || '';
        }
    }

    _handleKeyDown(e) {
        if (e.code === 'KeyP' && e.altKey) {
            e.preventDefault();
            this.toggleConsole();
            return;
        }

        if (this.consoleOpen) return;

        if (this.state.getGameState() === 'menu') {
            if (e.code === 'ArrowRight') {
                e.preventDefault();
                this._selectNextMap();
                return;
            }
            if (e.code === 'ArrowLeft') {
                e.preventDefault();
                this._selectPrevMap();
                return;
            }
        }

        if (e.code === 'Escape' && this.state.getGameState() === 'playing') {
            e.preventDefault();
            this.pause();
            return;
        }

        if (this.paused || this.state.getGameState() !== 'playing') return;

        // Weapon change with keys 1-3
        if (['Digit1', 'Digit2', 'Digit3'].includes(e.code)) {
            const weaponMap = {
                'Digit1': 'fists',
                'Digit2': 'sword',
                'Digit3': 'axe'
            };
            this._sendWeaponChange(weaponMap[e.code]);
            return;
        }

        this.keys[e.code] = true;
        this._sendInput();

        if (e.code === 'Space') {
            e.preventDefault();
            this._sendAttack();
        }

        if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
            e.preventDefault();
        }
    }

    _handleKeyUp(e) {
        if (this.consoleOpen || this.paused || this.state.getGameState() !== 'playing') return;
        this.keys[e.code] = false;
        this._sendInput();
    }

    _connect() {
        const statusEl = document.getElementById('connection-status');
        
        try {
            this.ws = new WebSocket(WS_URL);
            
            this.ws.onopen = () => {
                console.log('Connected to server');
                if (statusEl) {
                    statusEl.textContent = 'CONECTADO';
                    statusEl.classList.add('connected');
                    statusEl.classList.remove('hidden');
                }
                this._send({ type: 'get_state' });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleServerMessage(data);
                } catch (e) {
                    console.error('Error parsing state:', e);
                }
            };
            
            this.ws.onclose = () => {
                console.log('Disconnected from server');
                if (statusEl) {
                    statusEl.textContent = 'DESCONECTADO';
                    statusEl.classList.remove('connected');
                }
                setTimeout(() => this._connect(), 2000);
            };
            
            this.ws.onerror = (err) => {
                console.error('WebSocket error:', err);
            };
            
        } catch (e) {
            console.error('Failed to connect:', e);
            setTimeout(() => this._connect(), 2000);
        }
    }

    _handleServerMessage(data) {
        if (data.type === 'maps_list' || data.type === 'map_changed' || data.type === 'map_selected') {
            this._updateMapSelector(data);
            return;
        }
        
        if (data.game_state !== undefined) {
            this.state.updateFromServer(data);
            this._updateUI();
            
            const gameState = data.game_state;
            
            if (gameState === 'menu') {
                this._showScreen('menu');
            } else if (gameState === 'playing') {
                if (!this.paused) {
                    this._showScreen('none');
                }
                this._showHud(true);
            } else if (gameState === 'victory') {
                this._showScreen('victory');
                this._showHud(false);
            } else if (gameState === 'defeat') {
                this._showScreen('defeat');
                this._showHud(false);
            }
        }
    }

    _send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    _sendInput() {
        this._send({ type: 'input', keys: this.keys });
    }

    _sendAttack() {
        this._send({ type: 'attack' });
    }

    _sendWeaponChange(weapon) {
        this._send({ type: 'change_weapon', weapon: weapon });
    }

    start() {
        this.paused = false;
        this._showScreen('none');
        this._showHud(true);
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            if (this.state.getGameState() === 'menu') {
                this._send({ type: 'start' });
            } else {
                this._send({ type: 'resume' });
            }
        }
    }

    resume() {
        if (this.paused) {
            this.paused = false;
            this._showScreen('none');
            this._showHud(true);
            this._send({ type: 'resume' });
        }
    }

    pause() {
        if (this.state.getGameState() === 'playing' && !this.paused && !this.consoleOpen) {
            this.paused = true;
            this._showScreen('pause');
        }
    }

    returnToMenu() {
        this.state.gameState = 'menu';
        this.paused = false;
        this._showScreen('menu');
        this._showHud(false);
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this._send({ type: 'menu' });
        }
    }

    toggleConsole() {
        this.consoleOpen = !this.consoleOpen;
        const consoleEl = document.getElementById('console');
        if (consoleEl) {
            if (this.consoleOpen) {
                consoleEl.classList.remove('hidden');
                document.getElementById('console-input')?.focus();
                this.keys = {};
                this._sendInput();
            } else {
                consoleEl.classList.add('hidden');
                document.getElementById('console-input')?.blur();
            }
        }
    }

    _showScreen(screenId) {
        ['menu', 'victory', 'defeat', 'pause'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });
        
        if (screenId && screenId !== 'none') {
            const el = document.getElementById(screenId);
            if (el) el.classList.remove('hidden');
        }
    }

    _showHud(show) {
        ['hud', 'crosshair', 'kill-count', 'fps-counter'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                if (show) el.classList.remove('hidden');
                else el.classList.add('hidden');
            }
        });
        
        // Mostrar botones de arma durante el juego
        const weaponButtons = document.getElementById('weapon-buttons');
        if (weaponButtons) {
            if (show) weaponButtons.classList.remove('hidden');
            else weaponButtons.classList.add('hidden');
        }
    }

    _updateUI() {
        const killsEl = document.getElementById('kills');
        if (killsEl) killsEl.textContent = this.state.kills || 0;
        
        const fill = document.getElementById('health-fill');
        if (fill && this.state.player) {
            fill.style.width = Math.max(0, this.state.player.health) + '%';
            fill.style.background = this.state.player.health > 50 ? '#00ff00' : 
                                    this.state.player.health > 25 ? '#ffff00' : '#ff0000';
        }
    }

    _showDamageFlash() {
        const flash = document.getElementById('damage-flash');
        if (flash) {
            flash.style.opacity = 1;
            setTimeout(() => flash.style.opacity = 0, 150);
        }
    }

    _startRenderLoop() {
        let lastTime = 0;
        const render = (timestamp) => {
            this._updateFPS(timestamp);
            this._render();
            requestAnimationFrame(render);
        };
        requestAnimationFrame(render);
    }

    _render() {
        const canvas = document.getElementById('game');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        if (typeof renderFrame === 'function') {
            renderFrame(ctx, this.state);
        }
    }

    _updateFPS(timestamp) {
        if (!this._frameCount) {
            this._frameCount = 0;
            this._lastFpsTime = 0;
        }
        
        this._frameCount++;
        if (timestamp - this._lastFpsTime >= 1000) {
            const fps = this._frameCount;
            this._frameCount = 0;
            this._lastFpsTime = timestamp;
            
            const fpsEl = document.getElementById('fps-counter');
            if (fpsEl) fpsEl.textContent = `FPS: ${fps}`;
        }
    }
}

// Initialize the game when DOM is ready
let game = null;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        game = new Game();
    });
} else {
    game = new Game();
}
