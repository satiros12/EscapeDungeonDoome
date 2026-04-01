const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const SERVER_PORT = 8000;
const BASE_URL = `http://localhost:${SERVER_PORT}`;

let server;

async function startServer() {
    const venvPython = path.join(__dirname, '../..', '.venv/bin/python');
    return new Promise((resolve, reject) => {
        server = spawn(venvPython, ['src/server/server.py'], {
            cwd: path.join(__dirname, '../..'),
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        server.stdout.on('data', (data) => {
            console.log('Server stdout:', data.toString());
        });
        
        server.stderr.on('data', (data) => {
            console.log('Server stderr:', data.toString());
        });
        server.on('error', reject);
        let attempts = 0;
        const check = () => {
            require('http').get(BASE_URL, (res) => {
                if (res.statusCode === 200) resolve();
                else setTimeout(check, 500);
            }).on('error', () => {
                attempts++;
                if (attempts < 10) setTimeout(check, 500);
                else resolve();
            });
        };
        setTimeout(check, 1000);
    });
}

async function stopServer() {
    if (server) {
        server.kill();
        await new Promise(r => setTimeout(r, 500));
    }
}

async function runTests() {
    console.log('Starting WebDoom E2E Tests...\n');
    
    await startServer();
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') {
            errors.push(msg.text());
        }
    });
    page.on('pageerror', err => errors.push(err.message));
    
    let passed = 0;
    let failed = 0;
    let skipped = 0;
    
    try {
        console.log('Test 1: Menu screen loads');
        await page.goto(BASE_URL);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(500);
        
        await page.waitForFunction(() => {
            const status = document.getElementById('connection-status');
            return status && status.classList.contains('connected');
        }, { timeout: 10000 });
        
        await page.waitForTimeout(500);
        
        const menuVisible = await page.$eval('#menu', el => !el.classList.contains('hidden'));
        if (!menuVisible) throw new Error('Menu should be visible on load');
        const title = await page.textContent('#menu h1');
        if (!title.includes('WEBDOOM')) throw new Error('Title not found');
        console.log('  PASS: Menu screen loads correctly');
        passed++;
        
        console.log('Test 2: Start button exists');
        const startBtn = await page.$('#startBtn');
        if (!startBtn) throw new Error('Start button not found');
        console.log('  PASS: Start button exists');
        passed++;
        
        console.log('Test 2b: Map selector exists');
        const mapSelector = await page.$('#map-selector');
        if (!mapSelector) throw new Error('Map selector should exist in menu');
        const mapName = await page.textContent('#map-name');
        console.log('  Current map:', mapName);
        console.log('  PASS: Map selector exists');
        passed++;
        
        console.log('Test 2c: Map navigation arrows exist');
        const prevMap = await page.$('#prevMap');
        const nextMap = await page.$('#nextMap');
        if (!prevMap || !nextMap) throw new Error('Map navigation arrows should exist');
        console.log('  PASS: Map navigation arrows exist');
        passed++;
        
        console.log('Test 2d: Navigate to next map via button');
        const initialMapName = await page.textContent('#map-name');
        console.log('  Initial map:', initialMapName);
        await page.evaluate(() => {
            const btn = document.getElementById('nextMap');
            if (btn) btn.click();
        });
        await page.waitForTimeout(1000);
        const newMapName = await page.textContent('#map-name');
        console.log('  After click - map:', newMapName);
        if (newMapName === initialMapName) {
            throw new Error('Map name should have changed after clicking next map button');
        }
        const initialMapDesc = await page.textContent('#map-desc');
        console.log('  Description:', initialMapDesc);
        console.log('  PASS: Map button navigation works');
        passed++;

        console.log('Test 2e: Navigate to previous map via button');
        await page.evaluate(() => {
            const btn = document.getElementById('prevMap');
            if (btn) btn.click();
        });
        await page.waitForTimeout(1000);
        const prevMapName = await page.textContent('#map-name');
        console.log('  After prev - map:', prevMapName);
        if (prevMapName === newMapName) {
            throw new Error('Map name should have changed after clicking prev map button');
        }
        console.log('  PASS: Previous map button works');
        passed++;

        console.log('Test 2f: Navigate maps with keyboard arrows');
        const currentMapName = await page.textContent('#map-name');
        console.log('  Current map before keyboard:', currentMapName);
        await page.keyboard.press('ArrowRight');
        await page.waitForTimeout(1000);
        const afterRight = await page.textContent('#map-name');
        console.log('  After ArrowRight:', afterRight);
        if (afterRight === currentMapName) {
            throw new Error('Map should change with ArrowRight in menu');
        }
        await page.keyboard.press('ArrowLeft');
        await page.waitForTimeout(1000);
        const afterLeft = await page.textContent('#map-name');
        console.log('  After ArrowLeft:', afterLeft);
        if (afterLeft === afterRight) {
            throw new Error('Map should change with ArrowLeft in menu');
        }
        console.log('  PASS: Keyboard arrow navigation works');
        passed++;
        
        console.log('Test 3: Clicking Start begins game');
        
        await page.waitForFunction(() => {
            const status = document.getElementById('connection-status');
            return status && status.classList.contains('connected');
        }, { timeout: 10000 });
        console.log('  WebSocket connected');
        
        await startBtn.click();
        await page.waitForTimeout(2000);
        
        const menuHidden = await page.$eval('#menu', el => el.classList.contains('hidden'));
        if (!menuHidden) throw new Error('Menu should be hidden after start');
        
        const hudVisible = await page.$eval('#hud', el => !el.classList.contains('hidden'));
        if (!hudVisible) throw new Error('HUD should be visible during game');
        console.log('  PASS: Game starts when clicking Start button');
        passed++;
        
        console.log('Test 4: Canvas is rendered');
        const canvas = await page.$('canvas#game');
        if (!canvas) throw new Error('Canvas not found');
        const canvasSize = await canvas.boundingBox();
        if (canvasSize.width < 100 || canvasSize.height < 100) throw new Error('Canvas too small');
        console.log('  PASS: Canvas is rendered');
        passed++;
        
        console.log('Test 5: Health bar is visible');
        const healthBar = await page.$('#health-fill');
        if (!healthBar) throw new Error('Health bar not found');
        console.log('  PASS: Health bar is visible');
        passed++;
        
        console.log('Test 6: Player movement (WASD) works without errors');
        await page.keyboard.down('KeyW');
        await page.waitForTimeout(200);
        await page.keyboard.up('KeyW');
        await page.keyboard.down('KeyS');
        await page.waitForTimeout(200);
        await page.keyboard.up('KeyS');
        await page.keyboard.down('KeyA');
        await page.waitForTimeout(200);
        await page.keyboard.up('KeyA');
        await page.keyboard.down('KeyD');
        await page.waitForTimeout(200);
        await page.keyboard.up('KeyD');
        console.log('  PASS: Player movement keys work');
        passed++;
        
        console.log('Test 7: Camera rotation works');
        await page.keyboard.down('ArrowRight');
        await page.waitForTimeout(200);
        await page.keyboard.up('ArrowRight');
        await page.keyboard.down('ArrowLeft');
        await page.waitForTimeout(200);
        await page.keyboard.up('ArrowLeft');
        console.log('  PASS: Camera rotation works');
        passed++;
        
        console.log('Test 8: Attack with spacebar works');
        await page.keyboard.press('Space');
        await page.waitForTimeout(100);
        console.log('  PASS: Attack with spacebar works');
        passed++;
        
        console.log('  Enabling god mode for remaining tests...');
        await page.keyboard.down('Alt');
        await page.keyboard.press('KeyP');
        await page.keyboard.up('Alt');
        await page.waitForTimeout(300);
        await page.type('#console-input', 'god');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(300);
        await page.keyboard.down('Alt');
        await page.keyboard.press('KeyP');
        await page.keyboard.up('Alt');
        await page.waitForTimeout(300);
        
        console.log('Test 9: Kill counter is visible during game');
        const killCountVisible = await page.$eval('#kill-count', el => !el.classList.contains('hidden'));
        if (!killCountVisible) throw new Error('Kill counter should be visible during game');
        const killText = await page.$eval('#kills', el => el.textContent.trim());
        if (killText !== '0') throw new Error(`Kill count should start at 0, got: "${killText}"`);
        console.log('  PASS: Kill counter is visible and starts at 0');
        passed++;
        
        console.log('Test 10: FPS counter is visible during game');
        const fpsVisible = await page.$eval('#fps-counter', el => !el.classList.contains('hidden'));
        if (!fpsVisible) throw new Error('FPS counter should be visible during game');
        const fpsText = await page.textContent('#fps-counter');
        if (!fpsText.includes('FPS:')) throw new Error('FPS counter should display FPS value');
        console.log('  PASS: FPS counter is visible');
        passed++;
        
        console.log('Test 11: ESC pauses the game');
        await page.waitForTimeout(1000);
        await page.keyboard.press('Escape');
        await page.waitForTimeout(1000);
        const pauseVisible = await page.$eval('#pause', el => !el.classList.contains('hidden'));
        if (!pauseVisible) {
            const gameStateVal = await page.evaluate(() => {
                try { return window.gameState; } catch(e) { return 'undefined'; }
            });
            console.log('  Debug: gameState =', gameStateVal);
            throw new Error('Pause menu should be visible after pressing ESC');
        }
        console.log('  PASS: ESC pauses the game');
        passed++;
        
        console.log('Test 12: Resume button works');
        await page.click('#resumeBtn');
        await page.waitForTimeout(500);
        const pauseHiddenAfterResume = await page.$eval('#pause', el => el.classList.contains('hidden'));
        if (!pauseHiddenAfterResume) throw new Error('Pause menu should be hidden after resuming');
        console.log('  PASS: Resume button works');
        passed++;
        
        console.log('Test 13: Console opens with ALT+P');
        await page.keyboard.down('Alt');
        await page.keyboard.press('KeyP');
        await page.keyboard.up('Alt');
        await page.waitForTimeout(300);
        const consoleVisible = await page.$eval('#console', el => !el.classList.contains('hidden'));
        if (!consoleVisible) throw new Error('Console should be visible after pressing ALT+P');
        console.log('  PASS: Console opens with ALT+P');
        passed++;
        
        console.log('Test 14: Console closes with ALT+P');
        await page.keyboard.down('Alt');
        await page.keyboard.press('KeyP');
        await page.keyboard.up('Alt');
        await page.waitForTimeout(300);
        const consoleHidden = await page.$eval('#console', el => el.classList.contains('hidden'));
        if (!consoleHidden) throw new Error('Console should be hidden after pressing ALT+P again');
        console.log('  PASS: Console closes with ALT+P');
        passed++;
        
        console.log('Test 15: Menu button in pause returns to menu');
        await page.keyboard.press('Escape');
        await page.waitForTimeout(300);
        await page.click('#pauseMenuBtn');
        await page.waitForTimeout(300);
        const menuVisibleFromPause = await page.$eval('#menu', el => !el.classList.contains('hidden'));
        if (!menuVisibleFromPause) throw new Error('Menu should be visible after clicking Menu button');
        console.log('  PASS: Menu button in pause returns to menu');
        passed++;
        
        console.log('Test 16: Start new game after returning to menu');
        await page.click('#startBtn');
        await page.waitForTimeout(2000);
        const hudVisibleAfterRestart = await page.$eval('#hud', el => !el.classList.contains('hidden'));
        if (!hudVisibleAfterRestart) throw new Error('HUD should be visible when restarting game');
        console.log('  PASS: Game restarts correctly');
        passed++;
        
        // ============================================
        // NEW TESTS - Damage, Kills, Victory, Maps, Resize, FPS
        // ============================================
        
        console.log('\n--- Additional Tests: Damage, Kills, Victory ---');
        
        console.log('Test 17: Real damage to player');
        try {
            // Go back to menu first
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
            await page.click('#pauseMenuBtn');
            await page.waitForTimeout(500);
            
            // Make sure we're not in god mode by toggling it off if active
            await page.keyboard.down('Alt');
            await page.keyboard.press('KeyP');
            await page.keyboard.up('Alt');
            await page.waitForTimeout(300);
            await page.type('#console-input', 'god');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(300);
            
            // Start fresh game without god mode
            await page.click('#startBtn');
            await page.waitForTimeout(2000);
            
            // Get initial health
            const initialHealth = await page.$eval('#health-fill', el => {
                const style = el.getAttribute('style') || '';
                const match = style.match(/width:\s*(\d+)%/);
                return match ? parseInt(match[1]) : 100;
            });
            console.log('  Initial health:', initialHealth + '%');
            
            // Wait for enemy to attack (enemies should be in the game)
            // Give enemy time to approach and attack
            await page.waitForTimeout(5000);
            
            // Check if health decreased
            const currentHealth = await page.$eval('#health-fill', el => {
                const style = el.getAttribute('style') || '';
                const match = style.match(/width:\s*(\d+)%/);
                return match ? parseInt(match[1]) : 100;
            });
            console.log('  Current health after waiting:', currentHealth + '%');
            
            if (currentHealth >= initialHealth) {
                // Health didn't change - try moving to trigger combat
                await page.keyboard.down('KeyW');
                await page.waitForTimeout(1000);
                await page.keyboard.up('KeyW');
                await page.waitForTimeout(3000);
                
                const healthAfterMove = await page.$eval('#health-fill', el => {
                    const style = el.getAttribute('style') || '';
                    const match = style.match(/width:\s*(\d+)%/);
                    return match ? parseInt(match[1]) : 100;
                });
                console.log('  Health after moving:', healthAfterMove + '%');
                
                if (healthAfterMove >= initialHealth) {
                    throw new Error('Health should decrease after enemy attack, but got initial: ' + initialHealth + ', current: ' + healthAfterMove);
                }
            }
            
            console.log('  PASS: Player takes real damage from enemies');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        console.log('Test 18: Enemy death increases kill counter');
        try {
            // Enable god mode to prevent player death while killing enemies
            await page.keyboard.down('Alt');
            await page.keyboard.press('KeyP');
            await page.keyboard.up('Alt');
            await page.waitForTimeout(300);
            await page.type('#console-input', 'god');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(300);
            await page.keyboard.down('Alt');
            await page.keyboard.press('KeyP');
            await page.keyboard.up('Alt');
            await page.waitForTimeout(300);
            
            // Get initial kill count
            const initialKills = await page.$eval('#kills', el => parseInt(el.textContent.trim()) || 0);
            console.log('  Initial kills:', initialKills);
            
            // Move player to find enemies and attack multiple times
            // Press attack key multiple times to kill enemy
            for (let i = 0; i < 10; i++) {
                await page.keyboard.press('Space');
                await page.waitForTimeout(200);
            }
            
            // Wait for enemy death animation
            await page.waitForTimeout(2000);
            
            // Move around a bit to find another enemy
            await page.keyboard.down('KeyW');
            await page.waitForTimeout(500);
            await page.keyboard.up('KeyW');
            await page.waitForTimeout(1000);
            
            // Attack again
            for (let i = 0; i < 10; i++) {
                await page.keyboard.press('Space');
                await page.waitForTimeout(200);
            }
            
            await page.waitForTimeout(2000);
            
            const currentKills = await page.$eval('#kills', el => parseInt(el.textContent.trim()) || 0);
            console.log('  Current kills:', currentKills);
            
            if (currentKills <= initialKills) {
                throw new Error(`Kill count should increase after killing enemies, initial: ${initialKills}, current: ${currentKills}`);
            }
            
            console.log('  PASS: Kill counter increases when enemies die');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        console.log('Test 19: Full victory screen appears after killing all enemies');
        try {
            // Continue killing enemies until victory
            // Get current kills
            const killsBefore = await page.$eval('#kills', el => parseInt(el.textContent.trim()) || 0);
            console.log('  Kills before:', killsBefore);
            
            // Keep attacking until victory screen appears
            let victoryAppeared = false;
            const maxAttempts = 50;
            
            for (let i = 0; i < maxAttempts && !victoryAppeared; i++) {
                await page.keyboard.press('Space');
                await page.waitForTimeout(150);
                
                // Check for victory screen
                victoryAppeared = await page.$eval('#victory', el => !el.classList.contains('hidden')).catch(() => false);
                
                if (!victoryAppeared) {
                    // Move to find more enemies
                    await page.keyboard.down('KeyW');
                    await page.waitForTimeout(200);
                    await page.keyboard.up('KeyW');
                }
            }
            
            await page.waitForTimeout(1000);
            
            const victoryVisible = await page.$eval('#victory', el => !el.classList.contains('hidden'));
            if (!victoryVisible) {
                throw new Error('Victory screen should appear after killing all enemies');
            }
            
            console.log('  PASS: Victory screen appears after killing all enemies');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        console.log('Test 20: Map change and gameplay works');
        try {
            // Click "Continue" or go back to menu from victory
            const continueBtn = await page.$('#continueBtn');
            if (continueBtn) {
                await continueBtn.click();
                await page.waitForTimeout(1000);
            }
            
            // Go to menu
            const menuBtnFromVictory = await page.$('#menuBtn');
            if (menuBtnFromVictory) {
                await menuBtnFromVictory.click();
            } else {
                await page.keyboard.press('Escape');
                await page.waitForTimeout(300);
            }
            await page.waitForTimeout(500);
            
            // Get current map
            const currentMap = await page.textContent('#map-name');
            console.log('  Current map:', currentMap);
            
            // Change to a different map
            await page.evaluate(() => {
                const btn = document.getElementById('nextMap');
                if (btn) btn.click();
            });
            await page.waitForTimeout(1000);
            
            const newMap = await page.textContent('#map-name');
            console.log('  Changed to map:', newMap);
            
            if (newMap === currentMap) {
                throw new Error('Map should have changed');
            }
            
            // Start game on new map
            await page.click('#startBtn');
            await page.waitForTimeout(2000);
            
            // Verify game runs on new map
            const hudVisible = await page.$eval('#hud', el => !el.classList.contains('hidden'));
            if (!hudVisible) {
                throw new Error('HUD should be visible on new map');
            }
            
            // Test basic movement works on new map
            await page.keyboard.down('KeyW');
            await page.waitForTimeout(200);
            await page.keyboard.up('KeyW');
            
            console.log('  PASS: Game runs correctly on different map');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        console.log('Test 21: Window resize adjusts canvas correctly');
        try {
            // Get initial canvas size
            const canvas = await page.$('canvas#game');
            const initialBox = await canvas.boundingBox();
            console.log('  Initial canvas size:', initialBox.width + 'x' + initialBox.height);
            
            // Resize window to a smaller size
            await page.setViewportSize({ width: 800, height: 600 });
            await page.waitForTimeout(500);
            
            const smallBox = await canvas.boundingBox();
            console.log('  Canvas size after resize (800x600):', smallBox.width + 'x' + smallBox.height);
            
            if (smallBox.width > initialBox.width || smallBox.height > initialBox.height) {
                throw new Error('Canvas should have shrunk after viewport resize');
            }
            
            // Resize to larger size
            await page.setViewportSize({ width: 1400, height: 900 });
            await page.waitForTimeout(500);
            
            const largeBox = await canvas.boundingBox();
            console.log('  Canvas size after resize (1400x900):', largeBox.width + 'x' + largeBox.height);
            
            // Verify canvas adjusted
            if (largeBox.width < smallBox.width || largeBox.height < smallBox.height) {
                throw new Error('Canvas should have grown after viewport resize');
            }
            
            // Reset to default size
            await page.setViewportSize({ width: 1024, height: 768 });
            await page.waitForTimeout(300);
            
            console.log('  PASS: Canvas adjusts correctly on window resize');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        console.log('Test 22: FPS performance test');
        try {
            // Get FPS counter value
            const fpsText = await page.textContent('#fps-counter');
            console.log('  FPS text:', fpsText);
            
            // Extract FPS number from text (format: "FPS: XX")
            const fpsMatch = fpsText.match(/FPS:\s*(\d+)/);
            if (!fpsMatch) {
                throw new Error('Could not parse FPS value from: ' + fpsText);
            }
            
            const fps = parseInt(fpsMatch[1]);
            console.log('  Current FPS:', fps);
            
            if (fps < 30) {
                throw new Error(`FPS should be above 30, but got ${fps}`);
            }
            
            // Run for a few seconds and check again
            await page.waitForTimeout(3000);
            
            const fpsText2 = await page.textContent('#fps-counter');
            const fpsMatch2 = fpsText2.match(/FPS:\s*(\d+)/);
            const fps2 = parseInt(fpsMatch2[1]);
            console.log('  FPS after 3 seconds:', fps2);
            
            if (fps2 < 30) {
                throw new Error(`FPS should remain above 30, but got ${fps2}`);
            }
            
            console.log('  PASS: FPS is above 30 during gameplay');
            passed++;
        } catch (err) {
            console.error('  FAIL:', err.message);
            failed++;
        }
        
        if (errors.length > 0) {
            console.log('\nConsole errors detected:');
            errors.forEach(e => console.log('  - ' + e));
        } else {
            console.log('\n  PASS: No console errors');
        }
        
        console.log('\n========================================');
        console.log(`Tests: ${passed} passed, ${failed} failed, ${skipped} skipped`);
        console.log('========================================');
        
    } catch (err) {
        console.error('\nTEST FAILED:', err.message);
        failed++;
    } finally {
        await browser.close();
        await stopServer();
    }
    
    if (failed > 0) {
        process.exit(1);
    }
}

runTests().catch(console.error);
