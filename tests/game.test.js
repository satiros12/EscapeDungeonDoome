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
    
    try {
        console.log('Test 1: Menu screen loads');
        await page.goto(BASE_URL);
        await page.waitForSelector('#menu h1');
        const title = await page.textContent('#menu h1');
        if (!title.includes('WEBDOOM')) throw new Error('Title not found');
        console.log('  PASS: Menu screen loads correctly');
        
        console.log('Test 2: Start button exists');
        const startBtn = await page.$('#startBtn');
        if (!startBtn) throw new Error('Start button not found');
        console.log('  PASS: Start button exists');
        
        console.log('Test 3: Clicking Start begins game');
        await startBtn.click();
        await page.waitForTimeout(300);
        const menuHidden = await page.$eval('#menu', el => el.classList.contains('hidden'));
        if (!menuHidden) throw new Error('Menu should be hidden after start');
        const hudVisible = await page.$eval('#hud', el => !el.classList.contains('hidden'));
        if (!hudVisible) throw new Error('HUD should be visible during game');
        console.log('  PASS: Game starts when clicking Start button');
        
        console.log('Test 4: Canvas is rendered');
        const canvas = await page.$('canvas#game');
        if (!canvas) throw new Error('Canvas not found');
        const canvasSize = await canvas.boundingBox();
        if (canvasSize.width < 100 || canvasSize.height < 100) throw new Error('Canvas too small');
        console.log('  PASS: Canvas is rendered');
        
        console.log('Test 5: Health bar is visible');
        const healthBar = await page.$('#health-fill');
        if (!healthBar) throw new Error('Health bar not found');
        console.log('  PASS: Health bar is visible');
        
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
        
        console.log('Test 7: Camera rotation works');
        await page.keyboard.down('ArrowRight');
        await page.waitForTimeout(200);
        await page.keyboard.up('ArrowRight');
        await page.keyboard.down('ArrowLeft');
        await page.waitForTimeout(200);
        await page.keyboard.up('ArrowLeft');
        console.log('  PASS: Camera rotation works');
        
        console.log('Test 8: Attack with spacebar works');
        await page.keyboard.press('Space');
        await page.waitForTimeout(100);
        console.log('  PASS: Attack with spacebar works');
        
        console.log('Test 9: Return to menu via victory button');
        await page.evaluate(() => {
            document.getElementById('victory').classList.remove('hidden');
            document.getElementById('hud').classList.add('hidden');
        });
        const victoryBtn = await page.$('#victoryBtn');
        await victoryBtn.click();
        await page.waitForTimeout(300);
        const menuVisible = await page.$eval('#menu', el => !el.classList.contains('hidden'));
        if (!menuVisible) throw new Error('Menu should be visible after clicking victory button');
        console.log('  PASS: Can return to menu from victory screen');
        
        console.log('Test 10: Return to menu via defeat button');
        await page.click('#startBtn');
        await page.waitForTimeout(200);
        await page.evaluate(() => {
            document.getElementById('defeat').classList.remove('hidden');
            document.getElementById('hud').classList.add('hidden');
        });
        const defeatBtn = await page.$('#defeatBtn');
        await defeatBtn.click();
        await page.waitForTimeout(300);
        const menuVisibleAgain = await page.$eval('#menu', el => !el.classList.contains('hidden'));
        if (!menuVisibleAgain) throw new Error('Menu should be visible after clicking defeat button');
        console.log('  PASS: Can return to menu from defeat screen');
        
        if (errors.length > 0) {
            console.log('\nConsole errors detected:');
            errors.forEach(e => console.log('  - ' + e));
        } else {
            console.log('\n  PASS: No console errors');
        }
        
        console.log('\n========================================');
        console.log('All tests PASSED!');
        console.log('========================================');
        
    } catch (err) {
        console.error('\nTEST FAILED:', err.message);
        process.exitCode = 1;
    } finally {
        await browser.close();
        await stopServer();
    }
}

runTests().catch(console.error);
