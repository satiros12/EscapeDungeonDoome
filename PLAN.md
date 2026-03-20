# PLAN.md - WebDoom MVP

## Fase 1: Estructura base y rendering
### Tareas
- [ ] Crear archivo `index.html` con canvas a pantalla completa
- [ ] Implementar raycasting básico para renderizado de paredes
- [ ] Definir mapa del laberinto (grid 16x16 mínimo)
- [ ] Renderizar vista en primera persona con columnas de rayos
- [ ] Implementar movimiento del jugador (WASD)

### Criterios aceptación
- Canvas renderiza paredes con efecto de profundidad
- Jugador puede moverse por el mapa sin atravesar paredes
- No hay glitches de renderizado básicos

## Fase 2: Enemigos y IA
### Tareas
- [ ] Representar enemigos como sprites 2D proyectados
- [ ] Implementar patrulla aleatoria de enemigos
- [ ] Sistema de detección: enemigos "ven" al jugador en cierto rango y ángulo
- [ ] Implementar estado `chase`: enemigo persigue al jugador
- [ ] Implementar colisiones jugador-enemigo (daño mutuo)

### Criterios aceptación
- 3 enemigos visibles en el mapa
- Enemigos patrullan cuando jugador no está en rango
- Enemigos persiguen al detectar jugador

## Fase 3: Sistema de combate
### Tareas
- [ ] Implementar ataque con barra espaciadora
- [ ] Detectar si enemigo está en rango de golpe
- [ ] Aplicar daño a enemigo cercano (10 HP)
- [ ] Enemigos golpean al jugador cuando están en rango (10 HP)
- [ ] Cooldown de ataque (0.5s)

### Criterios aceptación
- Atravesar enemigo con barra espaciadora reduce su HP
- Enemigo que toca al jugador reduce su HP
- Feedback visual de daño recibido

## Fase 4: Estados de juego y UI
### Tareas
- [ ] Pantalla de menú inicial con botón Start
- [ ] Barra de vida del jugador en HUD
- [ ] Indicador de vida de enemigos
- [ ] Pantalla de victoria cuando todos los enemigos mueren
- [ ] Pantalla de derrota cuando HP jugador = 0
- [ ] Botón "Play Again" en pantallas finales

### Criterios aceptación
- Flujo completo: menu -> playing -> end -> menu
- HUD visible durante partida
- Estados de fin de juego muestran resultado correcto

## Fase 5: Polish y tests
### Tareas
- [ ] Añadir logging a `game.log`
- [ ] Tests E2E con Playwright
- [ ] Verificar que no hay errores en consola
- [ ] Optimizar rendimiento de raycasting

## Mapa del laberinto (propuesta 16x16)

```
################
#P.....#.......#
#.####.#.#####.#
#.#....#...#...#
#.#.#######.#.#
#.#........#.#.#
#.########.#.#.#
#........#.#.#.#
####.####.#.#...#
#E..#....#.#.### #
#.##.####.#.###.#
#....#....#.....#
#.####.######.###
#.#....#....#.E.#
#.#.##.####.#.###
#.....#....P#.E.#
################
```

## Detalles técnicos

### Raycasting
- Usar DDA (Digital Differential Analyzer) paraintersección rayos-pared
- FOV: 60 grados
- Distancia máxima: 16 unidades

### Sprites de enemigos
- Proyectar posición 3D a 2D en pantalla
- Ordenar por distancia (painter's algorithm inverso)
- Escalar según distancia

### Detección de jugador
- Rango de visión: 5 unidades
- Ángulo de visión: 90 grados (45° a cada lado)
- Line-of-sight bloqueada por paredes
