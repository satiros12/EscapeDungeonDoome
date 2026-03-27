/** NetworkManager - WebSocket handling with reconnection */

class NetworkManager {
    constructor(url = null) {
        this.url = url || WS_URL || 'ws://localhost:8001';
        this.ws = null;
        this.connected = false;
        this.reconnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 2000;
        
        this._listeners = new Map();
        this._messageQueue = [];
        
        this._setupEventListeners();
    }

    _setupEventListeners() {
        this._listeners.set('open', []);
        this._listeners.set('close', []);
        this._listeners.set('error', []);
        this._listeners.set('message', []);
    }

    on(event, callback) {
        if (!this._listeners.has(event)) {
            this._listeners.set(event, []);
        }
        this._listeners.get(event).push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (this._listeners.has(event)) {
            const callbacks = this._listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    _emit(event, data) {
        if (this._listeners.has(event)) {
            this._listeners.get(event).forEach(cb => {
                try {
                    cb(data);
                } catch (e) {
                    console.error(`Error in ${event} callback:`, e);
                }
            });
        }
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);
                
                this.ws.onopen = () => {
                    console.log('[Network] Connected');
                    this.connected = true;
                    this.reconnecting = false;
                    this.reconnectAttempts = 0;
                    this._emit('open');
                    this._flushMessageQueue();
                    resolve();
                };

                this.ws.onclose = (event) => {
                    console.log('[Network] Disconnected', event.code, event.reason);
                    this.connected = false;
                    this._emit('close', event);
                    
                    if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this._scheduleReconnect();
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('[Network] Error:', error);
                    this._emit('error', error);
                    reject(error);
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this._emit('message', data);
                    } catch (e) {
                        console.error('[Network] Failed to parse message:', e);
                    }
                };

            } catch (e) {
                reject(e);
            }
        });
    }

    _scheduleReconnect() {
        if (this.reconnecting) return;
        
        this.reconnecting = true;
        this.reconnectAttempts++;
        
        console.log(`[Network] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect().catch(() => {
                this._scheduleReconnect();
            });
        }, this.reconnectDelay);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }
        this.connected = false;
        this.reconnecting = false;
    }

    send(data) {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        
        if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            this._messageQueue.push(message);
        }
    }

    sendObject(obj) {
        this.send(JSON.stringify(obj));
    }

    _flushMessageQueue() {
        while (this._messageQueue.length > 0) {
            const message = this._messageQueue.shift();
            this.send(message);
        }
    }

    getState() {
        this.send({ type: 'get_state' });
    }

    sendInput(keys) {
        this.sendObject({ type: 'input', keys });
    }

    sendAction(action, data = {}) {
        this.sendObject({ type: 'action', action, ...data });
    }

    isConnected() {
        return this.connected;
    }
}


class ProtocolHandler {
    constructor(networkManager) {
        this.network = networkManager;
        this._lastState = null;
        this._deltaBuffer = new Map();
        
        networkManager.on('message', (data) => this._handleMessage(data));
    }

    _handleMessage(data) {
        if (data.type === 'state') {
            this._processState(data);
        } else if (data.type === 'event') {
            this._processEvent(data);
        } else if (data.type === 'sync') {
            this._processSync(data);
        }
    }

    _processState(message) {
        if (message.data.mode === 'full') {
            this._lastState = message.data;
            this._deltaBuffer.clear();
        } else if (message.data.mode === 'delta') {
            this._applyDelta(message.data.data);
        }
    }

    _applyDelta(deltaData) {
        if (!this._lastState) return;

        const changes = deltaData.changes || {};
        const removed = deltaData.removed || [];

        for (const [key, value] of Object.entries(changes)) {
            const keys = key.split('.');
            let obj = this._lastState;
            
            for (let i = 0; i < keys.length - 1; i++) {
                if (obj[keys[i]] === undefined) {
                    obj[keys[i]] = {};
                }
                obj = obj[keys[i]];
            }
            obj[keys[keys.length - 1]] = value;
        }

        for (const key of removed) {
            const keys = key.split('.');
            let obj = this._lastState;
            
            for (let i = 0; i < keys.length - 1; i++) {
                if (obj[keys[i]] === undefined) break;
                obj = obj[keys[i]];
            }
            delete obj[keys[keys.length - 1]];
        }
    }

    _processEvent(message) {
        console.log('[Protocol] Event:', message.event, message.data);
    }

    _processSync(message) {
        console.log('[Protocol] Sync:', message.timestamp);
    }

    getLastState() {
        return this._lastState;
    }
}
