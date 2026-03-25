# AGENTS.md

## Proyecto: WebDoom MVP - FPS Melee

### Stack
- HTML5 Canvas + JavaScript vanilla (en public/index.html)
- Python 3 + websockets + asyncio (en src/server/)
- Raycasting para gráficos pseudo-3D (estilo DOOM)
- Estructura modular: servidor separado del cliente

### Normas de código
1. Usa APIs modernas de Canvas y requestAnimationFrame
2. Gráficos simplificados: paredes de colores sólidos, enemigos como sprites 2D
3. Código conciso, sin sobreingeniería
4. Commit tras cada fase completada
5. Tests E2E con Playwright para verificar flujo de juego
6. Nunca hagas kill de todo python.
7. Estructura: public/ (frontend), src/server/ (backend), tests/ (tests)

### Arquitectura
```
WebDoom/
├── public/           # Frontend estático
│   └── index.html   # Cliente HTML5 Canvas
├── src/server/      # Servidor Python
│   ├── server.py    # HTTP + WebSocket server
│   ├── game_logic.py # IA, combate, movimiento
│   ├── game_state.py # Entidades, estado
│   └── physics.py   # Colisiones
├── tests/
│   └── e2e/         # Tests E2E con Playwright
├── docs/            # Documentación
├── package.json     # Dependencias npm (Playwright)
└── requirements.txt # Dependencias Python

### Normas de código
1. Usa APIs modernas de Canvas y requestAnimationFrame
2. Gráficos simplificados: paredes de colores sólidos, enemigos como sprites 2D
3. Código conciso, sin sobreingeniería
4. Commit tras cada fase completada
5. Tests E2E con Playwright para verificar flujo de juego
6. Logging a consola y fichero `game.log` con eventos importantes
7. Nunca hagas kill de todo python.

### Estados de juego
1. `menu` - Pantalla inicial con título y botón "Start"
2. `playing` - Partida en curso
3. `victory` - Pantalla de victoria (todos los enemigos eliminados)
4. `defeat` - Pantalla de derrota (vida jugador a 0%)

### Mecánicas de combate
- **Vida jugador**: 100 HP
- **Vida enemigos**: 30 HP cada uno (3 enemigos = 90 HP total)
- **Daño al golpear**: 10 HP por golpe
- **Rango de ataque**: distancia < 1.5 unidades
- **Velocidad ataque**: 0.5 segundos de cooldown
- **Velocidad movimiento**: media

### Feedback visual
- Flash rojo en pantalla cuando el jugador recibe daño
- Enemigos muestran animación de muerte
- Cadáver del enemigo permanece en el mapa tras morir

### Controles
| Tecla | Acción |
|-------|--------|
| W | Movimiento hacia adelante |
| S | Movimiento hacia atrás |
| A | Strafe izquierdo |
| D | Strafe derecho |
| Flecha Izquierda | Rotar cámara izquierda |
| Flecha Derecha | Rotar cámara derecha |
| Espacio | Atacar (golpe cuerpo a cuerpo) |

### Estructura de datos

**Jugador**
```
{ x, y, angle, health: 100, attackCooldown: 0 }
```

**Enemigo**
```
{ x, y, angle, health: 30, state: 'patrol'|'chase'|'attack'|'dying'|'dead', deathTimer: 0 }
```

**Mapa**: Array 2D de strings con caracteres:
- `#` = pared
- `.` = suelo transitable
- `P` = posición inicial jugador
- `E` = posición enemigos

### Flujo de datos
1. Cliente envía input (teclas) al servidor via WebSocket
2. Servidor procesa lógica (movimiento, IA, combate)
3. Servidor envía estado actualizado al cliente
4. Cliente renderiza el estado
