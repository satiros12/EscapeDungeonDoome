# Black Screen Diagnostic Plan

## Problem Summary

The game starts with the menu correctly, but after clicking "COMENZAR" (START), the screen goes black with approximately 1 FPS instead of showing the 3D game view.

## Root Cause Analysis

### Issue 1: Duplicate Game Systems (PRIMARY CAUSE)

The codebase has **TWO separate game systems** running simultaneously:

#### System 1: Old System (Currently Active)
- `public/js/main.js` - Entry point, calls `requestAnimationFrame(render)`
- `public/js/client.js` - WebSocket client, state management with global variables
- `public/js/ui.js` - Menu and HUD management
- `public/js/renderer.js` - Raycasting renderer with `render()` function

#### System 2: New System (Partially Implemented)
- `public/js/game.js` - Game class with its own WebSocket, state management, and render loop

**Conflict**: Both systems:
- Create their own WebSocket connections
- Manage game state separately
- Run their own render loops
- Have event listeners for the same UI elements

### Issue 2: Missing renderFrame Function

In `public/js/game.js` line 476-478:
```javascript
if (typeof renderFrame === 'function') {
    renderFrame(ctx, this.state);
}
```

The `renderFrame` function **does not exist** in the codebase. This means the Game class's render method does nothing useful.

### Issue 3: Script Loading Order

In `public/index.html` lines 275-283:
```html
<script src="js/core/observable.js"></script>
<script src="js/core/game-state.js"></script>
<script src="js/config.js"></script>
<script src="js/renderer.js"></script>
<script src="js/game.js"></script>        <!-- New system - creates Game instance -->
<script src="js/client.js"></script>       <!-- Old system - creates globals -->
<script src="js/ui.js"></script>
<script src="js/input.js"></script>
<script src="js/main.js"></script>         <!-- Starts render loop -->
```

Both `game.js` and `main.js` initialize automatically, causing conflicts.

### Issue 4: State Synchronization Problems

- `client.js` uses global variables: `player`, `enemies`, `corpses`, `gameState`
- `game.js` uses `this.state` (GameState instance)
- The two systems are not synchronized
- When the server sends state updates, both systems may process them differently

### Issue 5: Potential 1 FPS Cause

The 1 FPS issue is likely caused by:
1. JavaScript errors in the render loop that are not properly caught
2. Conflicts between the two render loops competing for resources
3. The `updateFPS()` function in renderer.js might have issues

## Investigation Steps

### Step 1: Verify the Duplicate Systems

Check which systems are actually running:
1. Open browser DevTools (F12)
2. Check Console for errors
3. Look for multiple WebSocket connections in Network tab
4. Check if both `game` variable (from game.js) and global functions from client.js are active

### Step 2: Check for JavaScript Errors

1. Open browser DevTools > Console
2. Look for red error messages
3. Check for 404 errors loading scripts
4. Look for "renderFrame is not defined" or similar

### Step 3: Verify WebSocket Connections

1. Open browser DevTools > Network > WS (WebSocket)
2. Filter by "ws://"
3. Look for multiple WebSocket connections to port 8001
4. Check if messages are being sent/received correctly

### Step 4: Check Game State

1. In DevTools Console, type:
   - `game` (should show Game instance from game.js)
   - `gameState` (should show string from client.js)
   - `player` (should show player object)
2. Compare values from both systems

### Step 5: Check Renderer State

1. In DevTools Console, type:
   - `currentGrid` - should contain the map
   - `player` - should have valid x, y, angle
   - `enemies` - should be an array

## Proposed Solutions

### Solution A: Disable New System (Quick Fix)

Remove or comment out the game.js initialization in index.html:

```html
<!-- Comment out or remove this line -->
<!-- <script src="js/game.js"></script> -->
```

**Pros**: Quick fix, uses existing working system
**Cons**: Loses new features from game.js

### Solution B: Integrate Both Systems (Recommended)

1. Remove duplicate WebSocket connections
2. Make game.js use the global variables from client.js
3. Make renderer.js the primary renderer
4. Remove duplicate event listeners

### Solution C: Full Rewrite (Long Term)

1. Choose one system as the base
2. Migrate all features to that system
3. Remove the duplicate code

## Testing Plan

### Test 1: Verify Menu Works
1. Start the server: `python src/server/server.py`
2. Open http://localhost:8000
3. Verify menu is displayed correctly
4. Verify map selector works

### Test 2: Verify Black Screen Issue
1. Click "COMENZAR" button
2. Observe black screen with 1 FPS
3. Check DevTools Console for errors

### Test 3: Apply Fix
1. Apply one of the solutions above
2. Repeat Test 1 and Test 2
3. Verify game renders correctly

### Test 4: Verify Gameplay
1. Move with arrow keys
2. Attack with spacebar
3. Verify enemies appear and can be killed
4. Verify HUD updates correctly

## Files to Modify

1. `public/index.html` - Remove duplicate script or integrate systems
2. `public/js/game.js` - Either remove or integrate with old system
3. `public/js/client.js` - May need modifications for integration
4. `public/js/renderer.js` - May need error handling improvements

## References

- Previous working version: Check git history for commits before the issue appeared
- Key commits that may have introduced the issue:
  - `1e0ff63` - Fix: include game.js script in index.html
  - `060cf81` - Implement A* pathfinding for enemies
  - `d5bbec5` - Add advanced enemy types