# WebDoom Project Review

## Current State Summary

**Fecha de revisión:** 2026-03-25  
**Estado:** 16/16 tests passing ✅  
**Stack:** Python Server + HTML5 Canvas Client

---

## 1. Estado del Proyecto

### 1.1 Arquitectura Actual
```
WebDoom/
├── index.html          (28KB - cliente: rendering, UI, WebSocket client)
├── server.py          (9KB - servidor: lógica juego, WebSocket server)
├── game_logic.py     (8KB - IA enemigos, movimiento, combate)
├── game_state.py     (4KB - estado del juego, entidades)
├── physics.py        (2KB - colisiones, línea de vista)
├── tests/
│   └── game.test.js  (264 líneas - E2E tests con Playwright)
├── package.json
├── requirements.txt
└── *.md              (documentación)
```

### 1.2 Stack Tecnológico
- **Servidor:** Python 3 + websockets + asyncio
- **Cliente:** HTML5 Canvas + Vanilla JavaScript
- **Tests:** Playwright (E2E)
- **Puerto HTTP:** 8000
- **Puerto WebSocket:** 8001

### 1.3 Funcionalidades Implementadas
| Feature | Estado |
|---------|--------|
| Raycasting 3D | ✅ |
| Menú principal | ✅ |
| HUD (vida, kills, FPS) | ✅ |
| Movimiento WASD | ✅ |
| Rotación cámara | ✅ |
| Ataque cuerpo a cuerpo | ✅ |
| IA enemigos (patrol/chase/attack) | ✅ |
| Sistema de combate | ✅ |
| Pausa (ESC) | ✅ |
| Consola (ALT+P) | ✅ |
| Comandos: god, heal, kill, spawn | ✅ |
| Victorias/Derrotas | ✅ |

---

## 2. Análisis de Tests

### 2.1 Cobertura Actual (16 tests)

| # | Test | Estado | Área |
|---|------|--------|------|
| 1 | Menu screen loads | ✅ PASS | UI |
| 2 | Start button exists | ✅ PASS | UI |
| 3 | Clicking Start begins game | ✅ PASS | UI+State |
| 4 | Canvas is rendered | ✅ PASS | Rendering |
| 5 | Health bar is visible | ✅ PASS | UI |
| 6 | Player movement (WASD) | ✅ PASS | Input |
| 7 | Camera rotation | ✅ PASS | Input |
| 8 | Attack with spacebar | ✅ PASS | Input |
| 9 | Kill counter visible | ✅ PASS | UI |
| 10 | FPS counter visible | ✅ PASS | UI |
| 11 | ESC pauses game | ✅ PASS | UI |
| 12 | Resume button works | ✅ PASS | UI |
| 13 | Console opens ALT+P | ✅ PASS | UI |
| 14 | Console closes ALT+P | ✅ PASS | UI |
| 15 | Menu button returns to menu | ✅ PASS | UI |
| 16 | Start new game after return | ✅ PASS | Flow |

### 2.2 Tests Faltantes (No implementados)
- ❌ Test de victoria (matar todos los enemigos)
- ❌ Test de derrota (jugador muere)
- ❌ Tests unitarios de lógica Python
- ❌ Tests de colisión
- ❌ Tests de IA de enemigos

---

## 3. Estructura de Archivos - Propuesta de Reorganización

### 3.1 Estado Actual (Plano)
Todos los archivos en raíz:
```
WebDoom/
├── *.py          (4 archivos)
├── *.js          (0 - todo en HTML)
├── *.html        (1 archivo)
├── *.md          (7 archivos)
├── tests/
└── node_modules/
```

### 3.2 Estructura Propuesta

```
WebDoom/
├── public/
│   └── index.html          # Frontend (solo render + UI)
├── src/
│   ├── server/
│   │   ├── __init__.py
│   │   ├── server.py       # HTTP + WebSocket server
│   │   ├── game_logic.py   # IA, combate, movimiento
│   │   ├── game_state.py   # Entidades, estado
│   │   └── physics.py      # Colisiones
│   └── client/
│       └── js/
│           ├── renderer.js  # Raycasting, sprites
│           ├── ui.js        # HUD, menús
│           └── client.js    # WebSocket, input
├── tests/
│   ├── e2e/
│   │   └── game.test.js
│   └── unit/
│       ├── test_physics.py
│       ├── test_ai.py
│       └── test_combat.py
├── docs/
│   ├── AGENTS.md
│   ├── COMMANDS.md
│   └── ARCHITECTURE.md
├── package.json
├── requirements.txt
└── README.md
```

### 3.3 Beneficios de la Reorganización
1. **Separación de responsabilidades** - Server/Client claramente separados
2. **Escalabilidad** - Fácil añadir más módulos
3. **Mantenibilidad** - Código más fácil de navegar
4. **Tests** - Estructura clara para tests unitarios

---

## 4. Archivos Innecesarios a Eliminar

### 4.1 Archivos de Desarrollo/Logs (Eliminar)
| Archivo | Razón |
|---------|-------|
| `server.log` | Log temporal del servidor |
| `server_debug.log` | Debug temporal (600KB+) |
| `game.log` | Log del juego |
| `.ruff_cache/` | Cache de linter |
| `.ipynb_checkpoints/` | Checkpoints de Jupyter |
| `__pycache__/` | Cache de Python |
| `test-results/` | Resultados de tests Playwright |

### 4.2 Archivos de Node (Mantener)
| Archivo | Razón |
|---------|-------|
| `node_modules/` | Dependencias (commitear o .gitignore) |
| `package.json` | Dependencias npm |
| `package-lock.json` | Lock de versiones |

### 4.3 Documentación (Consolidar)
| Archivo | Acción |
|---------|--------|
| `PLAN.md` | Eliminar - obsoleto |
| `QUESTIONS.md` | Eliminar - obsoleto |
| `FEATURE.md` | Eliminar - obsoleto |
| `TEST.md` | Integrar en TESTS.md |
| `TESTS.md` | Mantener |
| `COMMANDS.md` | Mantener |
| `AGENTS.md` | Mantener |
| `REVIEW.md` | Mantener (este archivo) |

---

## 5. Proceso de Reorganización

### Fase 1: Preparación (No modificar código)
1. [ ] Crear carpetas: `public/`, `src/server/`, `src/client/`, `tests/unit/`, `docs/`
2. [ ] Mover documentación a `docs/`
3. [ ] Mover Python a `src/server/`
4. [ ] Mover HTML a `public/`
5. [ ] Extraer JS de HTML a `src/client/js/`
6. [ ] Crear estructura de tests unitarios

### Fase 2: Migración (Mantener funcionando)
1. [ ] Actualizar imports en Python
2. [ ] Actualizar paths en server.py
3. [ ] Actualizar paths en tests
4. [ ] Actualizar package.json scripts

### Fase 3: Limpieza
1. [ ] Eliminar archivos innecesarios (sección 4.1)
2. [ ] Consolidar documentación
3. [ ] Actualizar .gitignore
4. [ ] Commit de reorganización

### Fase 4: Validación
1. [ ] Ejecutar `npm test` - debe pasar
2. [ ] Verificar servidor inicia
3. [ ] Verificar cliente conecta
4. [ ] Verificar todas las features funcionan

---

## 6. Resumen de Cambios Recomendados

| Acción | Prioridad | Esfuerzo |
|--------|-----------|-----------|
| Eliminar logs/cache | Alta | Bajo |
| Reorganizar carpetas | Media | Medio |
| Consolidar docs | Media | Bajo |
| Añadir tests unitarios | Baja | Alto |
| Extraer JS de HTML | Baja | Medio |

---

## 7. Estado Actual vs Propuesta

| Aspecto | Actual | Propuesto |
|---------|--------|-----------|
| Estructura | Plana | Modular |
| Python | Raíz | src/server/ |
| HTML | Raíz | public/ |
| Docs | Raíz | docs/ |
| Tests E2E | tests/ | tests/e2e/ |
| Tests Unit | ❌ | tests/unit/ |
| Logs | En raíz | ❌ (eliminar) |
| Cache | En raíz | ❌ (eliminar) |

---

*Este documento describe el plan. No se ha realizado ningún cambio todavía.*
