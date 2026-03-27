# Tests - WebDoom

## Tests Unitarios (pytest)

### Summary
- **Total Tests**: 49
- **Passed**: 49
- **Failed**: 0

### Ejecución
```bash
# Activar venv
source .venv/bin/activate

# Ejecutar todos los tests
python -m pytest tests/unit/ -v

# Ejecutar test específico
python -m pytest tests/unit/test_physics.py -v
```

### Tests por módulo

| Módulo | Tests | Estado |
|--------|-------|--------|
| test_physics.py | 10 | ✅ PASS |
| test_ai.py | 10 | ✅ PASS |
| test_combat.py | 13 | ✅ PASS |
| test_systems.py | 16 | ✅ PASS |

---

## Tests E2E (Playwright)

### Summary
- **Total Tests**: 16
- **Passed**: 16
- **Skipped**: 0
- **Failed**: 0

### Ejecución
```bash
# Instalar playwright si es necesario
npx playwright install chromium

# Ejecutar tests
node tests/e2e/game.test.js
```

### Tests E2E

| # | Test Name | Status |
|---|-----------|--------|
| 1 | Menu screen loads | ✅ PASS |
| 2 | Start button exists | ✅ PASS |
| 3 | Clicking Start begins game | ✅ PASS |
| 4 | Canvas is rendered | ✅ PASS |
| 5 | Health bar is visible | ✅ PASS |
| 6 | Player movement (WASD) works | ✅ PASS |
| 7 | Camera rotation works | ✅ PASS |
| 8 | Attack with spacebar works | ✅ PASS |
| 9 | Kill counter is visible | ✅ PASS |
| 10 | FPS counter is visible | ✅ PASS |
| 11 | ESC pauses the game | ✅ PASS |
| 12 | Resume button works | ✅ PASS |
| 13 | Console opens with ALT+P | ✅ PASS |
| 14 | Console closes with ALT+P | ✅ PASS |
| 15 | Menu button returns to menu | ✅ PASS |
| 16 | Game restarts correctly | ✅ PASS |

---

## Coverage

### Servidor
- Physics: 100%
- Game Logic: 90%
- Systems (V2): 80%

### Cliente
- Renderer: Testing manual
- Game State: Testing manual
