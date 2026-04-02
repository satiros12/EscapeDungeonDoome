# AGENTS.md

## Proyecto: WebDoom - FPS Melee

### Stack
- HTML5 Canvas + JavaScript vanilla
- Python 3 + websockets + asyncio
- Raycasting para gráficos pseudo-3D (estilo DOOM)
- Arquitectura modular: servidor separado del cliente

### Normas de código
1. Usa APIs modernas de Canvas y requestAnimationFrame
2. Gráficos simplificados: paredes de colores sólidos, enemigos como sprites 2D
3. Código conciso, sin sobreingeniería
4. Commit tras cada fase completada
5. Tests E2E con Playwright + Tests unitarios con pytest
6. Nunca hagas kill de todo python
7. Estructura: public/ (frontend), src/server/ (backend), tests/ (tests)

### Arquitectura Actual (V2)
```
WebDoom/
├── public/                  # Frontend estático
│   ├── index.html          # Cliente HTML5 Canvas
│   └── js/
│       ├── main.js         # Entry point
│       ├── game.js         # Game facade
│       ├── core/           # Patrones (Observable, GameState)
│       ├── renderer.js     # Raycasting + sprites
│       ├── ui.js          # Menús, HUD
│       ├── input.js       # Manejo de teclas
│       └── client.js      # WebSocket client
├── src/server/             # Servidor Python
│   ├── server.py           # HTTP + WebSocket server
│   ├── game_engine.py      # GameEngine facade
│   ├── game_logic.py      # Lógica original (compatibilidad)
│   ├── game_state.py      # Entidades, estado
│   ├── physics.py         # Colisiones, línea de vista
│   ├── core/              # Interfaces abstractas
│   └── systems/           # Sistemas modulares
│       ├── player_system.py
│       ├── enemy_ai_system.py
│       └── combat_system.py
├── shared/                 # Constantes compartidas
│   ├── constants.py
│   ├── constants.js
│   └── map-data.json
├── tests/
│   ├── unit/              # Tests unitarios pytest
│   └── e2e/               # Tests E2E Playwright
└── docs/                  # Documentación
```

### Estados de juego
1. `menu` - Pantalla inicial
2. `playing` - Partida en curso
3. `victory` - Victoria (todos enemigos eliminados)
4. `defeat` - Derrota (jugador muerto)

### Mecánicas de combate
- **Vida jugador**: 100 HP
- **Vida enemigos**: 30 HP (3 enemigos)
- **Daño al golpear**: 10 HP
- **Rango de ataque**: < 1.5 unidades
- **Cooldown**: 0.5 segundos

### Controles
| Tecla | Acción |
|-------|--------|
| W | Movimiento adelante |
| S | Movimiento atrás |
| A | Strafe izquierdo |
| D | Strafe derecho |
| ← | Rotar izquierda |
| → | Rotar derecha |
| Espacio | Atacar |
| ESC | Pausa |
| ALT+P | Consola |

### Tests
```bash
# Unit tests
.venv/bin/python -m pytest tests/unit/ -v

# E2E tests
node tests/e2e/game.test.js
```

### Ejecutar servidor
```bash
.venv/bin/python src/server/server.py
```
