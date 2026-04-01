let gameState = 'menu';
let consoleOpen = false;
let paused = false;

function showScreen(screenId) {
    document.getElementById('menu').classList.add('hidden');
    document.getElementById('victory').classList.add('hidden');
    document.getElementById('defeat').classList.add('hidden');
    document.getElementById('pause').classList.add('hidden');
    document.getElementById('hud').classList.add('hidden');
    document.getElementById('crosshair').classList.add('hidden');
    document.getElementById('kill-count').classList.add('hidden');
    document.getElementById('fps-counter').classList.add('hidden');
    
    if (screenId && screenId !== 'none') {
        document.getElementById(screenId).classList.remove('hidden');
    }
}

function showDamageFlash() {
    const flash = document.getElementById('damage-flash');
    flash.style.opacity = 1;
    setTimeout(() => flash.style.opacity = 0, 150);
}

function updateHUD() {
    const fill = document.getElementById('health-fill');
    fill.style.width = Math.max(0, player.health) + '%';
    fill.style.background = player.health > 50 ? '#00ff00' : player.health > 25 ? '#ffff00' : '#ff0000';
    
    // Update weapon display
    const weaponNameEl = document.getElementById('weapon-name');
    const ammoCountEl = document.getElementById('ammo-count');
    if (weaponNameEl && player.current_weapon) {
        const weaponNames = {
            'fists': 'PUÑOS',
            'sword': 'ESPADA',
            'axe': 'HACHA'
        };
        weaponNameEl.textContent = weaponNames[player.current_weapon] || player.current_weapon.toUpperCase();
    }
    if (ammoCountEl) {
        ammoCountEl.textContent = '∞';
    }
}

function updateUI() {
    document.getElementById('kills').textContent = kills !== undefined ? kills : 0;
    
    if (player.health < CONFIG.PLAYER_MAX_HEALTH && player.health > 0) {
        const prevHealth = player.health;
        setTimeout(() => {
            if (player.health < prevHealth) {
                showDamageFlash();
            }
        }, 50);
    }
}

function startGame() {
    paused = false;
    
    showScreen('none');
    document.getElementById('hud').classList.remove('hidden');
    document.getElementById('crosshair').classList.remove('hidden');
    document.getElementById('kill-count').classList.remove('hidden');
    document.getElementById('fps-counter').classList.remove('hidden');
    
    console.log('startGame called, sending start to server');
    
    if (ws && ws.readyState === WebSocket.OPEN) {
        if (gameState === 'menu') {
            ws.send(JSON.stringify({ type: 'start' }));
            console.log('Start message sent to server (new game)');
        } else {
            ws.send(JSON.stringify({ type: 'resume' }));
            console.log('Resume message sent to server');
        }
    } else {
        console.log('WebSocket not open, state:', ws ? ws.readyState : 'ws is null');
    }
}

function returnToMenu() {
    gameState = 'menu';
    paused = false;
    showScreen('menu');
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'menu' }));
    }
}

function toggleConsole() {
    consoleOpen = !consoleOpen;
    const consoleEl = document.getElementById('console');
    if (consoleOpen) {
        consoleEl.classList.remove('hidden');
        document.getElementById('console-input').focus();
        keys = {};
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'input', keys: {} }));
        }
    } else {
        consoleEl.classList.add('hidden');
        document.getElementById('console-input').blur();
    }
}

function logToConsole(msg, type = '') {
    const output = document.getElementById('console-output');
    const line = document.createElement('div');
    line.className = type;
    line.textContent = '> ' + msg;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
}

function executeCommand(cmd) {
    const parts = cmd.trim().split(' ');
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);

    logToConsole(cmd, 'info');

    switch (command) {
        case 'help':
            logToConsole('Comandos disponibles:', 'info');
            logToConsole('  help - Mostrar esta ayuda', 'success');
            logToConsole('  status - Mostrar estado del juego', 'success');
            logToConsole('  heal - Curar al jugador (100 HP)', 'success');
            logToConsole('  kill - Eliminar a todos los enemigos', 'success');
            logToConsole('  spawn <x> <y> - Spawnear enemigo en posición', 'success');
            logToConsole('  god - Alternar modo dios', 'success');
            logToConsole('  speed <n> - Establecer velocidad (1-10)', 'success');
            logToConsole('  clear - Limpiar consola', 'success');
            break;
        case 'status':
            logToConsole(`Estado: ${gameState}`, 'info');
            logToConsole(`Jugador: x=${player.x.toFixed(2)}, y=${player.y.toFixed(2)}, angle=${player.angle.toFixed(2)}, health=${player.health}`, 'info');
            logToConsole(`Enemigos: ${enemies.length}`, 'info');
            logToConsole(`Paused: ${paused}`, 'info');
            logToConsole(`Console: ${consoleOpen ? 'abierta' : 'cerrada'}`, 'info');
            break;
        case 'heal':
            player.health = 100;
            updateHUD();
            logToConsole('Jugador curado (100 HP)', 'success');
            break;
        case 'kill':
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'console_command', command: 'kill_all' }));
                logToConsole('Enemigos eliminados', 'success');
            }
            break;
        case 'spawn':
            if (args.length >= 2) {
                const x = parseFloat(args[0]);
                const y = parseFloat(args[1]);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'console_command', command: 'spawn', x, y }));
                    logToConsole(`Enemigo spawneado en (${x}, ${y})`, 'success');
                }
            } else {
                logToConsole('Uso: spawn <x> <y>', 'error');
            }
            break;
        case 'god':
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'console_command', command: 'god' }));
                logToConsole('Modo dios activado', 'success');
            }
            break;
        case 'speed':
            if (args.length >= 1) {
                const speed = parseFloat(args[0]);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'console_command', command: 'speed', value: speed }));
                    logToConsole(`Velocidad establecida a ${speed}`, 'success');
                }
            } else {
                logToConsole('Uso: speed <n>', 'error');
            }
            break;
        case 'clear':
            document.getElementById('console-output').innerHTML = '';
            break;
        case '':
            break;
        default:
            logToConsole(`Comando desconocido: ${command}. Escribe "help" para ayuda.`, 'error');
    }
}

function pauseGame() {
    if (gameState === 'playing' && !paused && !consoleOpen) {
        paused = true;
        showScreen('pause');
        logToConsole('Juego pausado', 'info');
    }
}

function resumeGame() {
    if (paused) {
        paused = false;
        showScreen('none');
        document.getElementById('hud').classList.remove('hidden');
        document.getElementById('crosshair').classList.remove('hidden');
        document.getElementById('kill-count').classList.remove('hidden');
        document.getElementById('fps-counter').classList.remove('hidden');
        logToConsole('Juego reanudado', 'info');
    }
}

document.getElementById('startBtn').addEventListener('click', startGame);
document.getElementById('victoryBtn').addEventListener('click', returnToMenu);
document.getElementById('defeatBtn').addEventListener('click', returnToMenu);
document.getElementById('resumeBtn').addEventListener('click', resumeGame);
document.getElementById('pauseMenuBtn').addEventListener('click', returnToMenu);

document.getElementById('console-input').addEventListener('keydown', function(e) {
    if (e.code === 'Enter') {
        const cmd = this.value;
        this.value = '';
        executeCommand(cmd);
    }
});