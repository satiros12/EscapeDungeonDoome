# REVIEW.md - Map Selection Implementation

## Objective
Implement map selection in the game menu with carousel navigation and move configuration to JSON files.

---

## Tasks

### 1. Configuration Files
- [ ] Create `shared/config.json` with all game constants
- [ ] Create `shared/weapons.json` with weapon configurations
- [ ] Update server to load config from JSON
- [ ] Update client to load config from JSON

### 2. Maps Management
- [ ] Create `maps/` folder
- [ ] Move current map to `maps/base.json`
- [ ] Create 3 new maps:
  - `maps/arena.json` - Open combat arena
  - `maps/maze.json` - Complex maze
  - `maps/arena2.json` - Larger arena
- [ ] Update game state to handle multiple maps

### 3. Map Selection UI
- [ ] Update `index.html` with map selector in menu
- [ ] Add carousel navigation (left/right arrows)
- [ ] Display map preview/name
- [ ] Handle map selection on game start

### 4. Client Updates
- [ ] Update `game.js` to support map selection
- [ ] Update `client.js` to send selected map
- [ ] Update server to load requested map

### 5. Testing
- [ ] Add unit tests for map loading
- [ ] Add unit tests for config loading
- [ ] Run all tests

---

## Technical Details

### config.json Structure
```json
{
  "game": {
    "player_health": 100,
    "enemy_health": 30,
    "move_speed": 3,
    "rot_speed": 2
  },
  "weapons": { ... },
  "rendering": { ... }
}
```

### Map Structure
```json
{
  "name": "Base Map",
  "grid": ["########", "#......#", ...],
  "player_start": { "x": 1.5, "y": 1.5 },
  "enemy_count": 3
}
```

### UI Flow
1. Menu shows map carousel
2. Left/Right arrows change map
3. Start button loads selected map

---

## Estimated Time
- Configuration: 30 min
- Maps: 30 min
- UI: 45 min
- Testing: 15 min
