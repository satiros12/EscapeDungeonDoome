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

## 8. Tareas Pendientes (Post-Reorganización)

### 8.1 Extraer JS de HTML a `src/client/js/`

**Objetivo:** Separar el JavaScript embebido en `index.html` en módulos independientes.

**Archivos a crear:**
```
src/client/js/
├── renderer.js    # Raycasting, renderizado de paredes y sprites
├── sprites.js     # Enemigos, cadáveres, efectos visuales
├── input.js       # Teclado (WASD, flechas, espacio, ESC, ALT)
├── ui.js          # HUD, menús, consola
└── client.js      # WebSocket, sincronización con servidor
```

**Pasos:**
1. [ ] Crear carpeta `src/client/js/`
2. [ ] Extraer código de raycasting a `renderer.js`
3. [ ] Extraer lógica de sprites a `sprites.js`
4. [ ] Extraer manejo de input a `input.js`
5. [ ] Extraer UI (menú, pausa, consola) a `ui.js`
6. [ ] Extraer WebSocket y lógica de cliente a `client.js`
7. [ ] Actualizar `public/index.html` para cargar módulos
8. [ ] Actualizar `package.json` scripts si es necesario
9. [ ] Verificar que todos los tests pasen

**Dependencias:** Ninguna (vanilla JS)

---

### 8.2 Crear Tests Unitarios en `tests/unit/`

**Objetivo:** Añadir tests unitarios para lógica Python del servidor.

**Archivos a crear:**
```
tests/unit/
├── __init__.py
├── test_physics.py   # Tests de colisiones y línea de vista
├── test_ai.py        # Tests de IA de enemigos
└── test_combat.py   # Tests de sistema de combate
```

**test_physics.py - Cobertura:**
- [ ] `is_wall()` - Detección de paredes
- [ ] `check_collision()` - Colisión jugador-pared
- [ ] `line_of_sight()` - Línea de vista entre entidades

**test_ai.py - Cobertura:**
- [ ] `update_enemy()` - Transiciones de estado
- [ ] `patrol_movement()` - Movimiento en patrulla
- [ ] `chase_player()` - Persecución del jugador
- [ ] `attack_player()` - Ataque al jugador

**test_combat.py - Cobertura:**
- [ ] `player_attack()` - Daño a enemigos
- [ ] `enemy_attack()` - Daño al jugador
- [ ] `check_victory()` - Condición de victoria
- [ ] `check_defeat()` - Condición de derrota

**Framework:** pytest

---

### 8.3 Consolidar Documentación

**Objetivo:** Unificar y limpiar la documentación.

**Acciones:**
1. [ ] Revisar `docs/AGENTS.md` - actualizar si es necesario
2. [ ] Revisar `docs/COMMANDS.md` - actualizar si es necesario
3. [ ] Revisar `docs/TESTS.md` - integrar info de TEST.md
4. [ ] Crear `docs/ARCHITECTURE.md` - descripción de la arquitectura
5. [ ] Crear `README.md` - guía de inicio rápido

**docs/ARCHITECTURE.md debe incluir:**
- Diagrama de arquitectura (texto)
- Flujo de datos cliente-servidor
- Protocolo WebSocket
- Estructura de archivos

**README.md debe incluir:**
- Requisitos
- Instalación
- Cómo ejecutar
- Controles
- Tests

---

### 8.4 Actualizar .gitignore

**Objetivo:** Excluir archivos innecesarios del repositorio.

**Contenido:**
```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
dist/
build/

# Entornos virtuales
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
game.log
server.log

# Node
node_modules/
package-lock.json

# Test results
test-results/
.playwright/
playwright-report/

# Cache
.ruff_cache/
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db
```

---

## 9. Plan de Ejecución

### Orden recomendado:

1. **Actualizar .gitignore** (5 min) - Prioridad: Alta
2. **Consolidar documentación** (30 min) - Prioridad: Media
3. **Crear tests unitarios** (2-3 horas) - Prioridad: Media
4. **Extraer JS de HTML** (2-3 horas) - Prioridad: Baja

### Notas:
- Los tests E2E ya funcionan (16/16 passing)
- La estructura de carpetas está creada
- El servidor sirve correctamente desde `public/`

---

*Última actualización: 2026-03-25*
