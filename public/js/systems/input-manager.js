/** InputManager - Unified input handling for keyboard, mouse, and touch */

class InputManager {
    constructor() {
        this.keys = {};
        this.keysPressed = {};
        this.keysJustPressed = {};
        
        this.mouse = {
            x: 0,
            y: 0,
            dx: 0,
            dy: 0,
            buttons: {},
            buttonsJustPressed: {},
            locked: false
        };
        
        this.touch = {
            active: false,
            x: 0,
            y: 0,
            startX: 0,
            startY: 0
        };
        
        this._boundKeyDown = this._onKeyDown.bind(this);
        this._boundKeyUp = this._onKeyUp.bind(this);
        this._boundMouseMove = this._onMouseMove.bind(this);
        this._boundMouseDown = this._onMouseDown.bind(this);
        this._boundMouseUp = this._onMouseUp.bind(this);
        this._boundTouchStart = this._onTouchStart.bind(this);
        this._boundTouchMove = this._onTouchMove.bind(this);
        this._boundTouchEnd = this._onTouchEnd.bind(this);
        
        this._inputCallbacks = [];
        this._enabled = true;
        
        this._setupEventListeners();
    }

    _setupEventListeners() {
        document.addEventListener('keydown', this._boundKeyDown);
        document.addEventListener('keyup', this._boundKeyUp);
        document.addEventListener('mousemove', this._boundMouseMove);
        document.addEventListener('mousedown', this._boundMouseDown);
        document.addEventListener('mouseup', this._boundMouseUp);
        document.addEventListener('touchstart', this._boundTouchStart, { passive: false });
        document.addEventListener('touchmove', this._boundTouchMove, { passive: false });
        document.addEventListener('touchend', this._boundTouchEnd);
    }

    destroy() {
        document.removeEventListener('keydown', this._boundKeyDown);
        document.removeEventListener('keyup', this._boundKeyUp);
        document.removeEventListener('mousemove', this._boundMouseMove);
        document.removeEventListener('mousedown', this._boundMouseDown);
        document.removeEventListener('mouseup', this._boundMouseUp);
        document.removeEventListener('touchstart', this._boundTouchStart);
        document.removeEventListener('touchmove', this._boundTouchMove);
        document.removeEventListener('touchend', this._boundTouchEnd);
    }

    _onKeyDown(e) {
        if (!this._enabled) return;
        
        const code = e.code;
        
        if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(code)) {
            e.preventDefault();
        }
        
        if (!this.keys[code]) {
            this.keysJustPressed[code] = true;
        }
        
        this.keys[code] = true;
        this._notifyCallbacks();
    }

    _onKeyUp(e) {
        if (!this._enabled) return;
        
        this.keys[e.code] = false;
        this._notifyCallbacks();
    }

    _onMouseMove(e) {
        if (!this._enabled) return;
        
        const rect = document.getElementById('game')?.getBoundingClientRect();
        if (rect) {
            this.mouse.x = e.clientX - rect.left;
            this.mouse.y = e.clientY - rect.top;
        }
        
        this.mouse.dx = e.movementX || 0;
        this.mouse.dy = e.movementY || 0;
    }

    _onMouseDown(e) {
        if (!this._enabled) return;
        
        this.mouse.buttons[e.button] = true;
        this.mouse.buttonsJustPressed[e.button] = true;
    }

    _onMouseUp(e) {
        if (!this._enabled) return;
        
        this.mouse.buttons[e.button] = false;
    }

    _onTouchStart(e) {
        if (!this._enabled) return;
        e.preventDefault();
        
        const touch = e.touches[0];
        const rect = document.getElementById('game')?.getBoundingClientRect();
        
        if (rect && touch) {
            this.touch.x = touch.clientX - rect.left;
            this.touch.y = touch.clientY - rect.top;
            this.touch.startX = this.touch.x;
            this.touch.startY = this.touch.y;
            this.touch.active = true;
        }
    }

    _onTouchMove(e) {
        if (!this._enabled) return;
        e.preventDefault();
        
        const touch = e.touches[0];
        const rect = document.getElementById('game')?.getBoundingClientRect();
        
        if (rect && touch) {
            this.touch.x = touch.clientX - rect.left;
            this.touch.y = touch.clientY - rect.top;
        }
    }

    _onTouchEnd(e) {
        if (!this._enabled) return;
        
        this.touch.active = false;
    }

    _notifyCallbacks() {
        const inputState = this.getInputState();
        this._inputCallbacks.forEach(cb => {
            try {
                cb(inputState);
            } catch (e) {
                console.error('Input callback error:', e);
            }
        });
    }

    onInput(callback) {
        this._inputCallbacks.push(callback);
        return () => {
            const index = this._inputCallbacks.indexOf(callback);
            if (index > -1) this._inputCallbacks.splice(index, 1);
        };
    }

    update() {
        this.keysJustPressed = {};
        this.mouse.buttonsJustPressed = {};
        this.mouse.dx = 0;
        this.mouse.dy = 0;
    }

    getInputState() {
        return {
            keys: { ...this.keys },
            keysJustPressed: { ...this.keysJustPressed },
            mouse: { ...this.mouse },
            touch: { ...this.touch }
        };
    }

    isKeyDown(code) {
        return !!this.keys[code];
    }

    isKeyJustPressed(code) {
        return !!this.keysJustPressed[code];
    }

    isMouseButtonDown(button) {
        return !!this.mouse.buttons[button];
    }

    isTouchActive() {
        return this.touch.active;
    }

    setEnabled(enabled) {
        this._enabled = enabled;
        if (!enabled) {
            this.keys = {};
            this.keysJustPressed = {};
            this.mouse.buttons = {};
            this.mouse.buttonsJustPressed = {};
            this.touch.active = false;
        }
    }

    isEnabled() {
        return this._enabled;
    }
}


class InputMapper {
    static KEY_MAPPING = {
        forward: 'KeyW',
        backward: 'KeyS',
        left: 'KeyA',
        right: 'KeyD',
        rotateLeft: 'ArrowLeft',
        rotateRight: 'ArrowRight',
        attack: 'Space',
        pause: 'Escape',
        console: 'KeyP',
        restart: 'KeyR'
    };

    static ACTION_KEYS = ['forward', 'backward', 'left', 'right', 'rotateLeft', 'rotateRight'];

    constructor(inputManager) {
        this.input = inputManager;
    }

    getMovement() {
        return {
            forward: this.input.isKeyDown(InputMapper.KEY_MAPPING.forward),
            backward: this.input.isKeyDown(InputMapper.KEY_MAPPING.backward),
            left: this.input.isKeyDown(InputMapper.KEY_MAPPING.left),
            right: this.input.isKeyDown(InputMapper.KEY_MAPPING.right),
            rotateLeft: this.input.isKeyDown(InputMapper.KEY_MAPPING.rotateLeft),
            rotateRight: this.input.isKeyDown(InputMapper.KEY_MAPPING.rotateRight)
        };
    }

    isAttackJustPressed() {
        return this.input.isKeyJustPressed(InputMapper.KEY_MAPPING.attack);
    }

    isPauseJustPressed() {
        return this.input.isKeyJustPressed(InputMapper.KEY_MAPPING.pause);
    }

    isConsoleJustPressed() {
        return this.input.isKeyJustPressed(InputMapper.KEY_MAPPING.console);
    }

    isRestartJustPressed() {
        return this.input.isKeyJustPressed(InputMapper.KEY_MAPPING.restart);
    }

    hasMovementInput() {
        const movement = this.getMovement();
        return Object.values(movement).some(v => v);
    }
}
