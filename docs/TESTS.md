# Tests - WebDoom (Pygame)

## Tests Unitarios (pytest)

### Summary
- **Total Tests**: 97
- **Passed**: 97
- **Skipped**: 2

### Ejecución
```bash
# Activar venv
source .venv/bin/activate

# Ejecutar todos los tests
python -m pytest tests/ -v

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
| test_config.py | 19 | ✅ PASS |
| test_pathfinding.py | 13 | ✅ PASS |
| test_game_loop.py | 8 | ✅ PASS |
| test_gameplay.py | 12 | ✅ PASS |

---

## Tests de Integración

### test_game_loop.py

| Test Name | Status |
|-----------|--------|
| Game starts in menu | ✅ PASS |
| Game starts playing | ✅ PASS |
| Player initial position | ✅ PASS |
| Enemies spawn from map | ✅ PASS |
| Player can take damage | ✅ PASS |
| Player dies at zero health | ✅ PASS |
| Enemy can die | ✅ PASS |
| Game can be won | ✅ PASS |

### test_gameplay.py

| Test Name | Status |
|-----------|--------|
| Player movement forward | ✅ PASS |
| Player movement backward | ✅ PASS |
| Player strafe | ✅ PASS |
| Player rotation | ✅ PASS |
| Attack cooldown | ✅ PASS |
| Enemy chase behavior | ✅ PASS |
| Enemy attack | ✅ PASS |
| Combat damage | ✅ PASS |
| Win condition | ✅ PASS |
| Physics collision | ✅ PASS |
| Line of sight | ✅ PASS |
| God mode | ✅ PASS |

---

## Coverage

### Src Modules
- **Physics**: 100%
- **Game State**: 90%
- **Systems (AI, Combat, Player)**: 85%
- **Event System**: 80%

---

## Tests que fueron eliminados

Los siguientes tests ya no aplican porque correspondían a la arquitectura web:
- Tests E2E de Playwright (eliminado)
- Tests de networking/WebSocket (eliminado)
- Tests de cliente JavaScript (eliminado)

---

## Ejecución de Tests

```bash
# Todos los tests con coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Solo unit tests
python -m pytest tests/unit/ -v

# Solo integration tests
python -m pytest tests/integration/ -v

# Test de módulo específico
python -m pytest tests/unit/test_physics.py -v
```

---

## Agregar nuevos tests

Para agregar tests al proyecto Pygame:

```python
# tests/unit/test_new_feature.py
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from engine.game_state import GameState

class TestNewFeature:
    def test_example(self):
        state = GameState()
        assert state.game_state == "menu"
```