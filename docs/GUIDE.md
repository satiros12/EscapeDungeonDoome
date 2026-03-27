# WebDoom - Complete Code Guide

## Overview

WebDoom is a DOOM-style FPS game with a client-server architecture:
- **Server**: Python 3 + WebSockets + asyncio (handles game logic, physics, AI)
- **Client**: HTML5 Canvas + Vanilla JavaScript (handles rendering, input, UI)

---

## Project Structure

```
WebDoom/
├── public/                     # Frontend (static files served by HTTP server)
│   ├── index.html             # HTML structure, CSS styles, UI elements
│   └── js/
│       ├── config.js          # Game constants, map data, WebSocket URL
│       ├── renderer.js        # Raycasting engine, sprite rendering
│       ├── client.js          # WebSocket connection, state synchronization
│       ├── input.js           # Keyboard handling, input sending
│       ├── ui.js              # Menus, HUD, console, game screens
│       └── main.js            # Entry point, game loop trigger
├── src/server/                 # Backend (Python)
│   ├── server.py              # HTTP + WebSocket server, game loop
│   ├── game_state.py          # Data classes, map parsing, entity management
│   ├── game_logic.py          # Player movement, enemy AI, combat system
│   └── physics.py            # Collision detection, line of sight, raycasting
├── tests/                      # Test files
│   └── e2e/
│       └── game.test.js       # Playwright E2E tests
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # Architecture diagram and details
│   ├── COMMANDS.md            # Console commands reference
│   ├── GUIDE.md               # This file - code documentation
│   ├── AGENTS.md              # Development guidelines
│   ├── REVIEW.md              # Project review and recommendations
│   └── TESTS.md               # Test documentation
├── package.json               # npm dependencies (Playwright)
├── requirements.txt           # Python dependencies
└── README.md                  # Quick start guide
```

---

## Server Components (Python)

### server.py - Main Server Entry Point

**Purpose**: Runs both HTTP and WebSocket servers, runs the game loop.

**Key Classes/Functions**:
- `LogHandler` - HTTP request handler for serving static files and client logging
- `GameServer` - Main server class that manages:
  - HTTP server (port 8000 by default)
  - WebSocket server (port 8001 by default)
  - Game state and logic instances
  - Client connections

**Game Loop** (runs at 60 FPS):
1. If game state is "playing", call `self.logic.update(dt)`
2. Broadcast game state to all connected clients
3. Sleep for 1/60 second

**WebSocket Message Types** (received from client):
| Message | Action |
|---------|--------|
| `input` | Update `state.pending_input` with pressed keys |
| `start` | Reset game and start playing |
| `attack` | Player attacks nearby enemies |
| `resume` | Resume paused game |
| `menu` | Return to main menu |
| `console_command` | Execute debug commands (god, heal, kill_all, speed) |
| `get_state` | Request current game state |

---

### game_state.py - Data Models

**Purpose**: Defines all game data structures and configuration constants.

**Classes**:

| Class | Purpose |
|-------|---------|
| `GameConfig` | Game constants (FOV, speeds, damage, health, etc.) |
| `Player` | Player entity (x, y, angle, health, attack_cooldown) |
| `Enemy` | Enemy entity (x, y, angle, health, state, patrol_dir) |
| `Corpse` | Dead enemy (x, y) |
| `HitEffect` | Visual hit indicator (x, y, timer) |
| `GameState` | Main state container with all entities |

**Map Format** (16x16 grid):
```
################  # = Wall
#              #  . = Floor (empty)
#   E    #     #  P = Player start
#        #     #  E = Enemy spawn
...
```

**Key Methods**:
- `parse_map()` - Scans map string array and spawns entities
- `reset()` - Resets game to initial state
- `to_dict()` - Serializes state to JSON-sendable dictionary

---

### game_logic.py - Core Game Mechanics

**Purpose**: Handles all game logic updates - movement, AI, combat.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `update(dt)` | Main update called every frame |
| `move_player(dt, keys)` | Updates player position based on keyboard input |
| `update_enemies(dt)` | Runs enemy AI state machine |
| `player_attack()` | Checks for enemies in range and deals damage |
| `update_dying_enemies(dt)` | Handles death animation |
| `update_hit_effects(dt)` | Updates visual hit indicators |
| `check_conditions()` | Checks win/lose conditions |

**Enemy AI States**:
| State | Behavior |
|-------|----------|
| `patrol` | Move randomly, change direction when hitting walls |
| `chase` | Move toward player if visible and within range |
| `attack` | Deal damage to player if in attack range |
| `dying` | Death animation (1 second) |
| `dead` | Becomes corpse, removed from active enemies |

**Combat System**:
- Player attack range: 1.5 units
- Player damage: 10 HP per hit
- Player attack cooldown: 0.5 seconds
- Enemy attack range: 1.0 units
- Enemy damage: 10 HP per hit
- Enemy attack cooldown: 1.0 seconds
- Enemy detection range: 5 units

---

### physics.py - Physics Engine

**Purpose**: Handles collision detection, line of sight, raycasting.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `is_wall(x, y)` | Returns true if position is a wall |
| `has_line_of_sight(x1, y1, x2, y2)` | Returns true if nothing blocks view between two points |
| `cast_ray(ray_angle, player_x, player_y)` | Casts a ray and returns distance and wall side |
| `check_collision(x, y)` | Checks if position collides with wall |

**Line of Sight Algorithm**:
- Walks from point A to B in small steps
- If any step hits a wall, return false
- If no wall found, return true

---

## Client Components (JavaScript)

### config.js - Configuration

**Purpose**: Game constants and map data shared across client modules.

**Key Variables**:
| Variable | Purpose |
|----------|---------|
| `CONFIG` | FOV, ray count, colors, etc. |
| `WS_URL` | WebSocket URL (host:8001) |
| `mapData` | 2D array of map characters |
| `MAP_WIDTH`, `MAP_HEIGHT` | Map dimensions |

---

### renderer.js - Rendering Engine

**Purpose**: Renders the 3D view using raycasting technique.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `resizeCanvas()` | Resizes canvas to window size |
| `isWall(x, y)` | Checks if position is a wall (client-side) |
| `castRay(rayAngle)` | Casts single ray, returns distance and side |
| `renderWalls()` | Renders all wall strips using raycasting |
| `renderFloor()` | Renders floor gradient |
| `renderCeiling()` | Renders ceiling solid color |
| `renderSprites()` | Renders enemies and corpses as 2D sprites |
| `renderHitEffects()` | Renders hit indicators |
| `render(timestamp)` | Main render loop called by requestAnimationFrame |

**Raycasting Algorithm**:
1. Cast `NUM_RAYS` (320) rays across the field of view
2. For each ray, step forward until hitting a wall
3. Calculate perpendicular distance to avoid fisheye effect
4. Scale wall height based on distance (closer = taller)
5. Apply shading based on distance and wall side (NS vs EW)

**Sprite Rendering**:
1. Calculate distance and angle to each sprite
2. Filter sprites in front of player and within FOV
3. Sort by distance (far to near)
4. Project to screen coordinates
5. Draw as circles with simple features (eyes, arms)

---

### client.js - Network Communication

**Purpose**: Manages WebSocket connection and state updates.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `connectWebSocket()` | Establishes connection to server |
| `updateFPS(timestamp)` | Counts frames for FPS display |
| `getWebSocket()` | Returns WebSocket instance |

**Message Handling**:
- Receives game state JSON from server
- Updates local variables: `gameState`, `player`, `enemies`, `corpses`, `kills`, `hitEffects`
- Calls `updateUI()` to refresh HUD

**Reconnection**:
- If connection lost, retries every 2 seconds

---

### input.js - Input Handling

**Purpose**: Captures keyboard input and sends to server.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `sendInput()` | Sends current key state to server |
| `sendAttack()` | Sends attack command to server |
| `getKeys()` | Returns current key state |

**Key Mappings**:
| Key | Action |
|-----|--------|
| W | Move forward |
| S | Move backward |
| A | Strafe left |
| D | Strafe right |
| ← | Rotate left |
| → | Rotate right |
| Space | Attack |
| ESC | Pause |
| ALT+P | Toggle console |

---

### ui.js - User Interface

**Purpose**: Manages menus, HUD, console, and game screens.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `showScreen(screenId)` | Shows/hides appropriate screen |
| `showDamageFlash()` | Triggers red screen flash |
| `updateHUD()` | Updates health bar color/width |
| `updateUI()` | Updates kill counter, checks damage |
| `startGame()` | Starts or resumes game |
| `returnToMenu()` | Returns to main menu |
| `toggleConsole()` | Opens/closes console |
| `executeCommand(cmd)` | Parses and runs console commands |
| `pauseGame()` | Pauses the game |
| `resumeGame()` | Resumes the game |

**Game Screens**:
- `menu` - Main menu with START button
- `playing` - No screen shown, HUD visible
- `pause` - Pause menu with RESUME and MENU buttons
- `victory` - Victory screen when all enemies killed
- `defeat` - Defeat screen when player dies

**Console Commands**:
- `help` - Show commands
- `status` - Show game state
- `heal` - Restore player health
- `kill` - Kill all enemies
- `god` - Toggle god mode
- `speed <n>` - Set speed multiplier
- `spawn <x> <y>` - Spawn enemy
- `clear` - Clear console

---

### main.js - Entry Point

**Purpose**: Initializes the game.

**Initialization Steps**:
1. Resize canvas to window size
2. Add resize listener
3. Show menu screen
4. Connect to WebSocket
5. Start render loop

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                        │
├─────────────────────────────────────────────────────────────────┤
│  input.js            client.js              renderer.js         │
│  ─────────           ─────────              ───────────         │
│  Key events ──────►  WebSocket.send ──────► Server              │
│                     ◄──────────────  game_state JSON              │
│                              │                                   │
│                              ▼                                   │
│                     Updates ◄──────────────► Canvas render      │
│                     variables          (raycasting)              │
│                                                                 │
│                     ui.js ◄───────────────► HTML UI elements    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    WebSocket (port 8001)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER (Python)                         │
├─────────────────────────────────────────────────────────────────┤
│  server.py                                                       │
│  ─────────                                                       │
│  ┌────────────────┐                                              │
│  │  Game Loop     │◄── 60 FPS timer                              │
│  │  (update)      │                                              │
│  └───────┬────────┘                                              │
│          │                                                      │
│  ┌───────▼────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ game_logic.py  │───►│ physics.py   │    │ game_state.py│   │
│  │                │    │              │    │              │   │
│  │ move_player()  │    │ is_wall()    │    │ Player       │   │
│  │ update_enemies │    │ has_LOS()    │    │ Enemy        │   │
│  │ player_attack  │    │ cast_ray()   │    │ Corpse       │   │
│  └────────┬────────┘    └──────────────┘    └──────────────┘   │
│           │                                                       │
│           ▼                                                       │
│  broadcast_state() ────► All clients via WebSocket              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Game Constants

**From game_state.py (Server)**:
| Constant | Value | Purpose |
|----------|-------|---------|
| FOV | π/3 (60°) | Field of view |
| MOVE_SPEED | 3 | Player movement speed |
| ROT_SPEED | 2 | Camera rotation speed |
| ATTACK_RANGE | 1.5 | Player attack range |
| ATTACK_COOLDOWN | 0.5s | Player attack delay |
| ENEMY_SPEED | 2.5 | Enemy chase speed |
| DETECTION_RANGE | 5 | Enemy sight range |
| PLAYER_MAX_HEALTH | 100 | Player HP |
| ENEMY_MAX_HEALTH | 30 | Enemy HP |
| PLAYER_DAMAGE | 10 | Damage per player hit |
| ENEMY_DAMAGE | 10 | Damage per enemy hit |

---

## Testing

**E2E Tests** (Playwright):
- Tests run in browser via Playwright
- Located in `tests/e2e/game.test.js`
- Run with `npm test`

**Current Test Coverage** (16 tests):
- Menu screen loads
- Start button exists
- Clicking Start begins game
- Canvas is rendered
- Health bar visible
- Player movement (WASD)
- Camera rotation
- Attack with spacebar
- Kill counter visible
- FPS counter visible
- ESC pauses game
- Resume button works
- Console opens with ALT+P
- Console closes with ALT+P
- Menu button returns to menu
- Start new game after return

---

## Troubleshooting

**Server won't start**:
- Check Python dependencies: `pip install -r requirements.txt`
- Check ports 8000 and 8001 are available

**Client can't connect**:
- Verify server is running
- Check browser console for WebSocket errors
- Ensure using correct WebSocket port (HTTP port + 1)

**Game runs slowly**:
- Check FPS counter in top-left
- Reduce NUM_RAYS in config.js for better performance

**Enemies not responding**:
- Check line of sight (physics.has_line_of_sight)
- Ensure detection range is appropriate

**No enemies visible**:
- Check map has 'E' characters
- Verify enemy spawn positions

---

## Extension Points

To extend the game:

1. **Add new enemy types**: Extend `Enemy` class in `game_state.py`, add new states in `game_logic.py`

2. **Add new weapons**: Add to `GameConfig`, implement attack logic in `game_logic.py`

3. **Add new maps**: Edit `MAP_DATA` array in `game_state.py`, ensure matching in `config.js`

4. **Add visual effects**: Extend `HitEffect` class or add new effect types

5. **Add multiplayer**: Server already supports multiple clients - just need to add player identification

6. **Add sound**: Use HTML5 Audio API in client, sync with server events

---

*Last updated: 2026-03-26*