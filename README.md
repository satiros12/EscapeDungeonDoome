# WebDoom

FPS estilo DOOM con arquitectura cliente-servidor usando raycasting pseudo-3D.

## Resumen del Proyecto

WebDoom es un juego de accion en primera persona que implementa el clasico estilo de DOOM utilizando tecnologia web moderna:

- **Cliente**: HTML5 Canvas + JavaScript vanilla con renderizado por raycasting
- **Servidor**: Python 3 + WebSockets + asyncio
- **Comunicacion**: Protocolo WebSocket con compresion delta para optimizacion de ancho de banda

## Caracteristicas

- Renderizado pseudo-3D mediante raycasting
- Sistema de combate cuerpo a cuerpo con multiples armas
- Inteligencia artificial de enemigos con estados (patrol, chase, attack)
- Sistema de armadura y objetos coleccionables
- Mapas extensos con mision (punto de inicio y objetivo)
- Controles tactiles para dispositivos moviles
- Consola de comandos para debugging

## Requisitos

- Python 3.8+
- Node.js 14+ (para tests)
- Navegador moderno con soporte WebSocket

## Instalacion

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node
npm install
```

## Como Ejecutar

```bash
# Puerto por defecto (HTTP: 8000, WebSocket: 8001)
./start.sh

# Puerto personalizado
python3 src/server/server.py --host 0.0.0.0 --port 5000 --ws-port 5001
```

Luego abre `http://localhost:8000` en tu navegador.

## Controles

### Teclado

| Tecla | Accion |
|-------|--------|
| W | Avanzar |
| S | Retroceder |
| A | Strafe izquierdo |
| D | Strafe derecho |
| ← | Rotar izquierda |
| → | Rotar derecha |
| Espacio | Atacar |
| ESC | Pausar |
| ALT+P | Consola |

### Tactil (Movil)

- Joystick virtual para movimiento
- Botones tactiles para ataque y rotacion

## Consola

Presiona `ALT+P` para abrir la consola. Comandos disponibles:

| Comando | Descripcion |
|---------|-------------|
| `help` | Ver todos los comandos |
| `heal` | Curar jugador al 100% |
| `god` | Activar/desactivar modo dios |
| `kill` | Matar todos los enemigos |
| `spawn <x> <y>` | Crear enemigo en posicion |
| `speed <n>` | Multiplicador de velocidad (1-10) |

## Arquitectura

```
WebDoom/
├── public/                          # Frontend estatico
│   ├── index.html                  # HTML principal + CSS
│   └── js/
│       ├── main.js                 # Punto de entrada
│       ├── game.js                 # Fachada del juego
│       ├── client.js               # Cliente WebSocket
│       ├── renderer.js             # Renderizado raycasting
│       ├── ui.js                   # Gestion de UI/HUD
│       ├── input.js                # Manejo de entrada
│       ├── config.js               # Configuracion del cliente
│       ├── core/
│       │   ├── game-state.js       # Estado observable
│       │   └── observable.js       # Patron observador
│       ├── systems/
│       │   ├── network-manager.js  # Gestion de red
│       │   └── input-manager.js    # Entrada unificada
│       └── rendering/
│           └── raycaster.js        # Motor de raycasting
│
├── src/server/                     # Servidor Python
│   ├── server.py                   # HTTP + WebSocket server
│   ├── game_state.py               # Estado del juego + MapManager
│   ├── game_logic.py               # Logica principal del juego
│   ├── physics.py                  # Colisiones, linea de vista
│   ├── pathfinding.py              # Algoritmo A* para enemigos
│   ├── config.py                   # Configuracion del servidor
│   ├── core/
│   │   ├── interfaces.py           # Interfaces abstractas
│   │   └── event_system.py         # Dispatcher de eventos
│   ├── systems/
│   │   ├── player_system.py        # Movimiento del jugador
│   │   ├── enemy_ai_system.py      # IA de enemigos
│   │   ├── combat_system.py        # Sistema de combate
│   │   └── weapon_system.py        # Armas y objetos
│   ├── networking/
│   │   └── protocol.py             # Compresion delta
│   └── factory/
│       └── entity_factory.py       # Creacion de entidades
│
├── maps/                           # Mapas JSON
│   ├── base.json                   # Base Complex (25x24)
│   ├── arena.json                  # Arena Master
│   ├── arena2.json                 # Arena 2
│   ├── maze.json                   # Labyrinth
│   └── mission.json                # Mission Impossible
│
├── shared/                         # Codigo compartido
│   ├── constants.py                # Constantes servidor
│   ├── constants.js                # Constantes cliente
│   └── protocol.json               # Esquema del protocolo
│
├── tests/
│   ├── unit/                       # Tests unitarios (pytest)
│   │   ├── test_physics.py
│   │   ├── test_ai.py
│   │   ├── test_combat.py
│   │   ├── test_systems.py
│   │   ├── test_config.py
│   │   └── test_pathfinding.py
│   └── e2e/
│       └── game.test.js            # Tests E2E (Playwright)
│
└── docs/                           # Documentacion
    ├── ARCHITECTURE.md             # Arquitectura detallada
    ├── AGENTS.md                   # Normas de desarrollo
    └── TESTS.md                    # Documentacion de tests
```

## Estados del Juego

| Estado | Descripcion |
|--------|-------------|
| `menu` | Pantalla inicial |
| `playing` | Partida en curso |
| `victory` | Victoria (todos los enemigos eliminados) |
| `defeat` | Derrota (jugador muerto) |
| `pause` | Juego en pausa |

## Mecanicas de Juego

### Jugador

- **Salud**: 100 HP
- **Velocidad de movimiento**: 3.0 unidades/segundo
- **Velocidad de rotacion**: 2.0 radianes/segundo

### Armas

| Arma | Tipo | Daño | Rango | Cooldown |
|------|------|------|-------|----------|
| Fists | Melee | 10 | 1.5 | 0.5s |
| Sword | Melee | 15 | 1.8 | 0.4s |
| Axe | Melee | 30 | 2.0 | 0.8s |

### Enemigos

| Tipo | Salud | Velocidad | Daño | Comportamiento |
|------|-------|-----------|------|----------------|
| Imp | 30 | 2.5 | 10 | Chase directo |
| Demon | 60 | 2.0 | 15 | Flanker |
| Cacodemon | 100 | 1.5 | 20 | Shooter (rango) |
| Soldier | 40 | 2.0 | 8 | Patrol |
| Chaingunner | 60 | 1.8 | 12 | Suppress |

### Armadura

| Tipo | Valor | Reduccion de daño |
|------|-------|-------------------|
| Light | 50 | 25% |
| Heavy | 100 | 50% |

## Tests

```bash
# Tests unitarios
source .venv/bin/activate
python -m pytest tests/unit/ -v

# Tests E2E
node tests/e2e/game.test.js
```

### Resultados de Tests

- **Unitarios**: 77 passed, 2 skipped
- **E2E**: 22 passed, 5 failed (timing issues)

## Mapas Disponibles

1. **Base Complex** - Mapa grande con multiples habitaciones
2. **Arena Master** - Arena de combate
3. **Arena 2** - Segunda arena
4. **Labyrinth** - Laberinto complejo
5. **Mission Impossible** - Mapa con mision (inicio → objetivo)

## Protocolo de Comunicacion

### Cliente → Servidor

```json
{ "type": "input", "keys": { "KeyW": true } }
{ "type": "start" }
{ "type": "attack" }
{ "type": "resume" }
{ "type": "menu" }
{ "type": "console_command", "command": "god" }
```

### Servidor → Cliente

```json
{
  "type": "state",
  "mode": "full",
  "data": {
    "game_state": "playing",
    "player": { "x": 1.5, "y": 1.5, "angle": 0, "health": 100 },
    "enemies": [...],
    "corpses": [...],
    "kills": 0,
    "grid": [...],
    "map_width": 25,
    "map_height": 24
  }
}
```

## Licencia

MIT