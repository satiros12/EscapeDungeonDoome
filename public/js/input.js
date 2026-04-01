let keys = {};
let isTouchDevice = false;
let joystickActive = false;
let joystickTouchId = null;
let joystickCenter = { x: 0, y: 0 };
let joystickMaxRadius = 50;

// Detectar dispositivo tactil
isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

// Mostrar controles tactiles si es dispositivo tactil
if (isTouchDevice) {
    const touchControls = document.getElementById('touch-controls');
    if (touchControls) {
        touchControls.classList.remove('hidden');
    }
}

// Inicializar joystick
function initJoystick() {
    const joystickBase = document.getElementById('joystick-base');
    const joystickKnob = document.getElementById('joystick-knob');
    
    if (!joystickBase || !joystickKnob) return;
    
    // Obtener posicion inicial del centro del joystick
    const baseRect = joystickBase.getBoundingClientRect();
    joystickCenter = {
        x: baseRect.left + baseRect.width / 2,
        y: baseRect.top + baseRect.height / 2
    };
    
    joystickBase.addEventListener('touchstart', handleJoystickStart, { passive: false });
    joystickBase.addEventListener('touchmove', handleJoystickMove, { passive: false });
    joystickBase.addEventListener('touchend', handleJoystickEnd, { passive: false });
    joystickBase.addEventListener('touchcancel', handleJoystickEnd, { passive: false });
}

function handleJoystickStart(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (joystickTouchId !== null) return;
    
    const touch = e.changedTouches[0];
    joystickTouchId = touch.identifier;
    joystickActive = true;
    
    updateJoystickPosition(touch);
}

function handleJoystickMove(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (!joystickActive) return;
    
    // Buscar el touch del joystick
    let touch = null;
    for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === joystickTouchId) {
            touch = e.changedTouches[i];
            break;
        }
    }
    
    if (touch) {
        updateJoystickPosition(touch);
    }
}

function handleJoystickEnd(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Buscar el touch del joystick
    for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === joystickTouchId) {
            resetJoystick();
            break;
        }
    }
}

function updateJoystickPosition(touch) {
    const joystickKnob = document.getElementById('joystick-knob');
    if (!joystickKnob) return;
    
    // Calcular distancia desde el centro
    let dx = touch.clientX - joystickCenter.x;
    let dy = touch.clientY - joystickCenter.y;
    
    // Limitar el movimiento al radio maximo
    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > joystickMaxRadius) {
        dx = (dx / distance) * joystickMaxRadius;
        dy = (dy / distance) * joystickMaxRadius;
    }
    
    // Mover el knob
    joystickKnob.style.left = `calc(50% + ${dx}px)`;
    joystickKnob.style.top = `calc(50% + ${dy}px)`;
    
    // Mapear a teclas
    updateKeysFromJoystick(dx, dy);
}

function updateKeysFromJoystick(dx, dy) {
    const deadzone = 10;
    const threshold = 30;
    
    // Resetear teclas de movimiento
    keys['KeyW'] = false;
    keys['KeyS'] = false;
    keys['KeyA'] = false;
    keys['KeyD'] = false;
    
    // Eje Y (W/S)
    if (dy < -threshold) {
        keys['KeyW'] = true;
    } else if (dy > threshold) {
        keys['KeyS'] = true;
    }
    
    // Eje X (A/D)
    if (dx < -threshold) {
        keys['KeyA'] = true;
    } else if (dx > threshold) {
        keys['KeyD'] = true;
    }
    
    sendInput();
}

function resetJoystick() {
    const joystickKnob = document.getElementById('joystick-knob');
    if (joystickKnob) {
        joystickKnob.style.left = '50%';
        joystickKnob.style.top = '50%';
    }
    
    joystickTouchId = null;
    joystickActive = false;
    
    // Resetear teclas de movimiento
    keys['KeyW'] = false;
    keys['KeyS'] = false;
    keys['KeyA'] = false;
    keys['KeyD'] = false;
    
    sendInput();
}

// Inicializar botones tactiles
function initTouchButtons() {
    const btnAttack = document.getElementById('btn-attack');
    const btnPause = document.getElementById('btn-pause');
    const btnRotateLeft = document.getElementById('btn-rotate-left');
    const btnRotateRight = document.getElementById('btn-rotate-right');
    
    if (btnAttack) {
        btnAttack.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleAttackButton();
        }, { passive: false });
    }
    
    if (btnPause) {
        btnPause.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handlePauseButton();
        }, { passive: false });
    }
    
    if (btnRotateLeft) {
        btnRotateLeft.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleRotateLeftButton(true);
        }, { passive: false });
        btnRotateLeft.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleRotateLeftButton(false);
        }, { passive: false });
    }
    
    if (btnRotateRight) {
        btnRotateRight.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleRotateRightButton(true);
        }, { passive: false });
        btnRotateRight.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleRotateRightButton(false);
        }, { passive: false });
    }
}

function handleAttackButton() {
    if (consoleOpen || paused || gameState !== 'playing') return;
    
    keys['Space'] = true;
    sendInput();
    sendAttack();
    
    // Resetear despues de un pequeno delay
    setTimeout(() => {
        keys['Space'] = false;
        sendInput();
    }, 100);
}

function handlePauseButton() {
    if (gameState === 'playing' && !paused) {
        pauseGame();
    }
}

function handleRotateLeftButton(pressed) {
    if (consoleOpen || paused || gameState !== 'playing') return;
    
    keys['ArrowLeft'] = pressed;
    sendInput();
}

function handleRotateRightButton(pressed) {
    if (consoleOpen || paused || gameState !== 'playing') return;
    
    keys['ArrowRight'] = pressed;
    sendInput();
}

// Inicializar controles tactiles cuando el DOM este listo
if (isTouchDevice) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initJoystick();
            initTouchButtons();
        });
    } else {
        initJoystick();
        initTouchButtons();
    }
}

// Event listeners tactiles para cambiar de mapa en el menu
function initMapSelectorTouch() {
    const prevMapBtn = document.getElementById('prevMap');
    const nextMapBtn = document.getElementById('nextMap');
    
    if (prevMapBtn) {
        prevMapBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            selectPrevMap();
        }, { passive: false });
    }
    
    if (nextMapBtn) {
        nextMapBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            selectNextMap();
        }, { passive: false });
    }
}

// Inicializar tactil del selector de mapas
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMapSelectorTouch);
} else {
    initMapSelectorTouch();
}

// Teclado
document.addEventListener('keydown', e => {
    if (e.code === 'KeyP' && e.altKey) {
        e.preventDefault();
        toggleConsole();
        return;
    }

    if (consoleOpen) {
        return;
    }

    if (gameState === 'menu') {
        if (e.code === 'ArrowRight') {
            e.preventDefault();
            selectNextMap();
            return;
        }
        if (e.code === 'ArrowLeft') {
            e.preventDefault();
            selectPrevMap();
            return;
        }
    }

    if (e.code === 'Escape' && gameState === 'playing') {
        e.preventDefault();
        pauseGame();
        return;
    }

    if (paused || gameState !== 'playing') {
        return;
    }

    // Weapon change with keys 1-3
    if (['Digit1', 'Digit2', 'Digit3'].includes(e.code)) {
        const weaponMap = {
            'Digit1': 'fists',
            'Digit2': 'sword',
            'Digit3': 'axe'
        };
        sendWeaponChange(weaponMap[e.code]);
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

function sendWeaponChange(weapon) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'change_weapon', weapon: weapon }));
    }
}

function getKeys() {
    return keys;
}
