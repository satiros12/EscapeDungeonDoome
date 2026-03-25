const keys = {};

document.addEventListener('keydown', e => {
    if (e.code === 'KeyP' && e.altKey) {
        e.preventDefault();
        toggleConsole();
        return;
    }

    if (consoleOpen) {
        return;
    }

    if (e.code === 'Escape' && gameState === 'playing') {
        e.preventDefault();
        pauseGame();
        return;
    }

    if (paused || gameState !== 'playing') {
        return;
    }

    keys[e.code] = true;
    sendInput();
    
    if (e.code === 'Space') {
        e.preventDefault();
        sendAttack();
    }
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
        e.preventDefault();
    }
});

document.addEventListener('keyup', e => {
    if (consoleOpen || paused || gameState !== 'playing') {
        return;
    }
    keys[e.code] = false;
    sendInput();
});

function sendInput() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'input', keys: keys }));
    }
}

function sendAttack() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'attack' }));
    }
}

function getKeys() {
    return keys;
}