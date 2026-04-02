# Plan de Transformación: WebDoom → Pygame

## 1. Resumen Ejecutivo

Este documento describe el plan para transformar el proyecto actual de WebDoom (FPS estilo DOOM basado en web) en una aplicación de escritorio utilizando Pygame. El objetivo es eliminar completamente las dependencias web (HTML5 Canvas, JavaScript, WebSockets) y crear un juego standalone ejecutable directamente.

**Estado actual**: Proyecto web con cliente JavaScript + servidor Python + WebSockets  
**Estado objetivo**: Juego de escritorio Pygame completamente autônomo

---

## 2. Análisis de Componentes a Migrar

### 2.1 Componentes a Eliminar

| Componente | Ubicación | Razón |
|------------|-----------|-------|
| `public/index.html` | Frontend web | Reemplazado por ventana Pygame |
| `public/js/*` | Cliente JavaScript | Reemplazado por código Pygame |
| `src/client/` | Cliente JS separado | No necesario |
| `public/js/rendering/raycaster.js` | Renderer JS | Reemplazado por renderer Pygame |
| `public/js/systems/network-manager.js` | WebSocket client | No necesario |
| `public/js/systems/input-manager.js` | Input JS | Reemplazado por Pygame input |
| `public/js/ui.js` | UI web | Reemplazado por Pygame |
| `src/server/server.py` (WebSocket) | HTTP+WebSocket server | No necesario |
| `src/server/networking/protocol.py` | Delta compression | No necesario |
| `shared/constants.js` | Constantes cliente | Duplicado |
| `package.json` | npm dependencies | No necesario |
| `tests/e2e/` | Tests Playwright | No aplicable |

### 2.2 Componentes a Conservar

| Componente | Ubicación | Acción |
|------------|-----------|--------|
| `src/server/game_engine.py` | GameEngine facade | Adaptar a Pygame |
| `src/server/game_state.py` | Estado del juego | Mover a nuevo módulo |
| `src/server/physics.py` | Colisiones, raycasting | Adaptar sin cambios mayores |
| `src/server/systems/*` | Sistemas de juego | Conservar lógica |
| `src/server/core/event_system.py` | Sistema de eventos | Conservar |
| `src/server/factory/entity_factory.py` | Factory de entidades | Adaptar |
| `shared/constants.py` | Constantes | Actualizar para Pygame |
| `shared/map-data.json` | Datos del mapa | Conservar |
| `tests/unit/` | Tests unitarios pytest | Actualizar paths |

---

## 3. Nueva Arquitectura Pygame

### 3.1 Estructura de Directorios Objetivo

```
WebDoomPygame/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada Pygame
│   ├── game.py                 # Game facade (reemplaza game.js)
│   ├── config.py               # Configuración (reemplaza config.js)
│   ├── input_handler.py        # Manejo de input (reemplaza input.js)
│   ├── renderer.py             # Renderer (reemplaza renderer.js)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── menu.py             # Menú principal
│   │   ├── hud.py              # Heads-up display
│   │   └── console.py          # Consola debug
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── game_engine.py     # GameEngine (migrado)
│   │   ├── game_state.py      # Estado (migrado)
│   │   └── event_system.py     # Eventos (migrado)
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── player_system.py   # (migrado)
│   │   ├── enemy_ai_system.py  # (migrado)
│   │   ├── combat_system.py    # (migrado)
│   │   └── weapon_system.py    # (migrado)
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── physics.py          # (migrado)
│   │   ├── collision.py        # Colisiones 2D
│   │   └── raycasting.py       # Raycasting 2D
│   ├── factory/
│   │   └── entity_factory.py   # (migrado)
│   └── sprites/
│       ├── __init__.py
│       ├── player.py
│       ├── enemy.py
│       └── walls.py
├── assets/
│   ├── sprites/                # Sprites del juego
│   ├── textures/               # Texturas
│   └── fonts/                  # Fuentes
├── data/
│   └── map-data.json           # (conservado)
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_physics.py
│   │   ├── test_ai.py
│   │   ├── test_combat.py
│   │   ├── test_systems.py
│   │   ├── test_renderer.py    # NUEVO: Tests renderer
│   │   └── test_input.py       # NUEVO: Tests input
│   └── integration/
│       ├── test_game_loop.py   # NUEVO: Tests ciclo juego
│       └── test_gameplay.py    # NUEVO: Tests jugabilidad
├── docs/
│   └── (documentación)
├── requirements.txt             # Dependencias Python
└── README.md
```

### 3.2 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PYGAME APPLICATION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      main.py (Entry Point)                      │   │
│  │  - pygame.init()                                                │   │
│  │  - Game loop (60 FPS)                                           │   │
│  │  - Event handling                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                       │
│                                ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Game (Facade)                              │   │
│  │  - state: GameState                                            │   │
│  │  - engine: GameEngine                                          │   │
│  │  - renderer: Renderer                                          │   │
│  │  - input: InputHandler                                          │   │
│  │  - ui: UIManager                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │              │            │              │                  │
│  ┌──────┴──────┐ ┌─────┴─────┐ ┌───┴────┐ ┌───────┴───────┐         │
│  │   Renderer  │ │ InputHandler│ │  UI   │ │  GameEngine   │         │
│  │             │ │            │ │       │ │               │         │
│  │ - Raycast  │ │ - Keyboard │ │-Menu  │ │ - player_sys  │         │
│  │ - Sprites  │ │ - Mouse    │ │-HUD   │ │ - enemy_sys   │         │
│  │ - Draw     │ │ - Gamepad  │ │-Console│ │ - combat_sys  │         │
│  └────────────┘ └────────────┘ └───────┘ └───────────────┘         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    GameEngine (Systems)                      │   │
│  ├─────────────────┬─────────────────┬─────────────────┬───────┤   │
│  │ PlayerSystem    │ EnemyAISystem   │ CombatSystem    │Physics│   │
│  └─────────────────┴─────────────────┴─────────────────┴───────┘   │
│                                │                                    │
│  ┌─────────────────────────────┴─────────────────────────────┐   │
│  │                    GameState (State)                         │   │
│  │  - player, enemies[], corpses[], map, game_mode             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Plan de Implementación

### Fase 1: Configuración Base (Semana 1)

#### Tarea 1.1: Crear estructura del proyecto
- [ ] Crear directorio `src/` con subdirectorios
- [ ] Crear directorio `assets/` y subdirectorios
- [ ] Crear directorio `data/`
- [ ] Copiar `shared/map-data.json` a `data/`
- [ ] Crear `requirements.txt` con dependencias

#### Tarea 1.2: Configurar requirements.txt
```python
# requirements.txt
pygame>=2.5.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

#### Tarea 1.3: Crear main.py básico
- [ ] Inicializar Pygame
- [ ] Crear ventana 800x600
- [ ] Implementar game loop básico
- [ ] Manejar eventos de salida

### Fase 2: Motor de Juego (Semana 2)

#### Tarea 2.1: Migrar GameEngine
- [ ] Copiar `src/server/game_engine.py` a `src/engine/game_engine.py`
- [ ] Adaptar imports (eliminar referencias a networking)
- [ ] Integrar con nuevo sistema de input

#### Tarea 2.2: Migrar GameState
- [ ] Copiar `src/server/game_state.py` a `src/engine/game_state.py`
- [ ] Mantener estructura de entidades
- [ ] Actualizar paths de constantes

#### Tarea 2.3: Migrar Sistemas
- [ ] Copiar sistemas de `src/server/systems/` a `src/systems/`
- [ ] Adaptar imports entre sistemas
- [ ] Eliminar referencias a networking/websockets

#### Tarea 2.4: Migrar Physics
- [ ] Copiar `src/server/physics.py` a `src/physics/physics.py`
- [ ] Mantener lógica de colisiones y raycasting
- [ ] Adaptar para coordenadas 2D

### Fase 3: Renderer y Gráficos (Semana 3)

#### Tarea 3.1: Implementar Renderer
- [ ] Crear `src/renderer.py`
- [ ] Implementar raycasting (migrar lógica de JS)
- [ ] Implementar renderizado de sprites
- [ ] Implementar renderizado de paredes
- [ ] Implementar ceiling/floor rendering

#### Tarea 3.2: Crear Sprites
- [ ] Crear sprites básicos para paredes (colores sólidos inicial)
- [ ] Crear sprite de jugador (representación 2D)
- [ ] Crear sprites de enemigos
- [ ] Implementar sistema de animación básica

#### Tarea 3.3: UI del Juego
- [ ] Crear `src/ui/menu.py` (menú principal)
- [ ] Crear `src/ui/hud.py` (barra de vida, contador kills, FPS)
- [ ] Crear `src/ui/console.py` (consola debug)

### Fase 4: Input y Controles (Semana 3)

#### Tarea 4.1: InputHandler
- [ ] Crear `src/input_handler.py`
- [ ] Implementar manejo de teclado (WASD, arrows, space)
- [ ] Implementar manejo de mouse (rotación)
- [ ] Soporte para joystick/gamepad (opcional)

#### Tarea 4.2: Integrar Input con GameEngine
- [ ] Conectar InputHandler a PlayerSystem
- [ ] Mapear teclas a acciones del juego

### Fase 5: Integración y Testing (Semana 4)

#### Tarea 5.1: Integrar Componentes
- [ ] Conectar Game loop con GameEngine
- [ ] Conectar Renderer con GameState
- [ ] Conectar Input con PlayerSystem
- [ ] Conectar UI con GameState

#### Tarea 5.2: Pruebas de Integración
- [ ] Verificar inicio del juego
- [ ] Verificar movimiento del jugador
- [ ] Verificar combate con enemigos
- [ ] Verificar estados de juego (menu, playing, victory, defeat)

---

## 5. Plan de Testing

### 5.1 Tests Unitarios (pytest)

#### Tests Existentes (Actualizar)
Los tests actuales en `tests/unit/` funcionarán con modificaciones menores:

| Test File | Contenido | Adaptación needed |
|-----------|-----------|-------------------|
| `test_physics.py` | Tests de física | Actualizar imports |
| `test_ai.py` | Tests de IA enemigo | Actualizar imports |
| `test_combat.py` | Tests de combate | Actualizar imports |
| `test_systems.py` | Tests de sistemas | Actualizar imports |
| `test_config.py` | Tests de configuración | Actualizar imports |

#### Nuevos Tests Unitarios

| Test File | Contenido |
|-----------|-----------|
| `test_renderer.py` | Tests del renderer |
| `test_input.py` | Tests del input handler |
| `test_game_state.py` | Tests del estado del juego |

### 5.2 Tests de Integración

| Test File | Contenido |
|-----------|-----------|
| `test_game_loop.py` | Tests del ciclo principal del juego |
| `test_gameplay.py` | Tests de jugabilidad |

### 5.3 Ejecución de Tests

```bash
# Todos los tests unitarios
python -m pytest tests/unit/ -v

# Tests con coverage
python -m pytest tests/unit/ -v --cov=src --cov-report=html

# Tests de integración
python -m pytest tests/integration/ -v

# Todos los tests
python -m pytest tests/ -v
```

### 5.4 Matriz de Cobertura

| Módulo | Tipo test | Cobertura objetivo |
|--------|-----------|---------------------|
| physics.py | Unit | 100% |
| game_state.py | Unit | 90% |
| systems/* | Unit | 90% |
| input_handler.py | Unit + Integration | 80% |
| renderer.py | Unit + Integration | 70% |
| game loop | Integration | 80% |

---

## 6. Migración de Tests Existentes

### 6.1 Actualizar imports en tests existentes

Los tests actuales referencian módulos en `src.server`. Debren actualizarse:

```python
# ANTES (web)
from src.server.physics import PhysicsEngine
from src.server.game_state import GameState
from src.server.systems.enemy_ai_system import EnemyAISystem

# DESPUÉS (pygame)
from src.physics.physics import PhysicsEngine
from src.engine.game_state import GameState
from src.systems.enemy_ai_system import EnemyAISystem
```

### 6.2 Tests a crear para Pygame

#### test_renderer.py
```python
import pytest
from src.renderer import Renderer

def test_renderer_initialization():
    """Test que el renderer se inicializa correctamente"""
    # ...

def test_raycasting_returns_walls():
    """Test que el raycasting retorna paredes"""
    # ...

def test_sprite_rendering_order():
    """Test que sprites se renderizan en orden correcto (painter's algorithm)"""
    # ...
```

#### test_input.py
```python
import pytest
from src.input_handler import InputHandler

def test_keyboard_input():
    """Test de input de teclado"""
    # ...

def test_mouse_rotation():
    """Test de rotación con mouse"""
    # ...

def test_key_mapping():
    """Test de mapeo de teclas"""
    # ...
```

#### test_game_loop.py
```python
import pytest
from src.main import Game

def test_game_initialization():
    """Test de inicialización del juego"""
    # ...

def test_game_state_transitions():
    """Test de transiciones de estado"""
    # ...
```

---

## 7. Eliminación de Componentes Web

### 7.1 Archivos a Eliminar

```bash
# Eliminar frontend web completo
rm -rf public/

# Eliminar cliente JS separado
rm -rf src/client/

# Eliminar tests E2E (Playwright)
rm -rf tests/e2e/

# Eliminar networking del servidor
rm -rf src/server/networking/

# Eliminar constants.js
rm shared/constants.js

# Eliminar package.json
rm package.json
rm package-lock.json
```

### 7.2 Archivos a Actualizar

| Archivo | Cambio |
|---------|--------|
| `src/server/server.py` | Eliminar (reemplazado por main.py) |
| `src/server/game_logic.py` | Eliminar si no se usa |
| `shared/constants.py` | Actualizar para Pygame |

---

## 8. Cronograma

| Fase | Duración | Entregable |
|------|-----------|-------------|
| Fase 1: Base | 1 semana | Estructura de proyecto, main.py funcional |
| Fase 2: Motor | 2 semanas | GameEngine, GameState, Systems, Physics |
| Fase 3: Graphics | 1 semana | Renderer, Sprites, UI |
| Fase 4: Input | 1 semana | InputHandler integrado |
| Fase 5: Testing | 1 semana | Tests pasando, juego jugable |
| **Total** | **6 semanas** | Juego completo |

---

## 9. Consideraciones Adicionales

### 9.1 Rendering
- Usar `pygame.draw.polygon` para paredes (representación 2D de raycasting)
- Sprites como `pygame.sprite.Sprite`
- UI con `pygame.font`

### 9.2 Rendimiento
- Target: 60 FPS
- Usar `pygame.time.Clock` para control de FPS
- Optimizar raycasting si es necesario

### 9.3 Retrocompatibilidad
- Mantener la lógica de juego (physics, AI, combat) lo más idéntica posible
- Solo cambiar la capa de presentación (web → Pygame)

---

## 10. Referencias

- Documentación Pygame: https://www.pygame.org/docs/
- Tests actuales: `tests/unit/`
- Arquitectura actual: `docs/ARCHITECTURE.md`

---

*Documento generado para transformación WebDoom → Pygame*