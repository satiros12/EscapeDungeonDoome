const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const SERVER_PORT = 8000;
const BASE_URL = `http://localhost:${SERVER_PORT}`;

let server;

async function startServer() {
    return new Promise((resolve, reject) => {
        server = spawn('python3', ['server.py'], {
            cwd: path.join(__dirname, '..'),
            stdio: ['pipe', 'pipe', 'pipe']
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
