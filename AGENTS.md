# AGENTS.md

## Proyecto: WebDoom MVP - FPS Melee

### Stack
- HTML5 Canvas + JavaScript vanilla
- Raycasting para gráficos pseudo-3D (estilo DOOM)
- Sin dependencias externas
- Estructura simple: un único archivo HTML con CSS/JS embebido

### Normas de código
1. Usa APIs modernas de Canvas y requestAnimationFrame
2. Gráficos simplificados: paredes de un color, enemigos como sprites 2D
3. Código conciso, sin sobreingeniería
4. Commit tras cada fase completada
5. Tests E2E con Playwright para verificar flujo de juego
6. Logging a consola y fichero `game.log` con eventos importantes

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
{ x, y, angle, health: 30, state: 'patrol'|'chase'|'attack'|'dead' }
```

**Mapa**: Array 2D de strings con caracteres:
- `#` = pared
- `.` = suelo transitable
- `P` = posición inicial jugador
- `E` = posición enemigos
