# Tests - WebDoom

## Tests E2E (Playwright)

### Summary
- **Total Tests**: 16
- **Passed**: 16
- **Skipped**: 0
- **Failed**: 0

### Ejecución
```bash
npm test
```

### Test Results

| # | Test Name | Status |
|---|-----------|--------|
| 1 | Menu screen loads | ✅ PASS |
| 2 | Start button exists | ✅ PASS |
| 3 | Clicking Start begins game | ✅ PASS |
| 4 | Canvas is rendered | ✅ PASS |
| 5 | Health bar is visible | ✅ PASS |
| 6 | Player movement (WASD) works without errors | ✅ PASS |
| 7 | Camera rotation works | ✅ PASS |
| 8 | Attack with spacebar works | ✅ PASS |
| 9 | Kill counter is visible during game | ✅ PASS |
| 10 | FPS counter is visible during game | ✅ PASS |
| 11 | ESC pauses the game | ✅ PASS |
| 12 | Resume button works | ✅ PASS |
| 13 | Console opens with ALT+P | ✅ PASS |
| 14 | Console closes with ALT+P | ✅ PASS |
| 15 | Menu button in pause returns to menu | ✅ PASS |
| 16 | Start new game after returning to menu | ✅ PASS |

### Notas
- God mode habilitado durante tests para evitar muerte del jugador
- Pantallas de victoria/derrota requieren testing manual

---

## Tests Unitarios (Pendientes)

### Objetivos
- Tests de física (colisiones, línea de vista)
- Tests de IA de enemigos
- Tests de sistema de combate

### Ubicación
```
tests/unit/
├── test_physics.py
├── test_ai.py
└── test_combat.py
```
