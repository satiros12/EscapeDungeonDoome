# PLAN.md - WebDoom MVP

## Resumen requisitos
- Colores sólidos simples
- Animación de muerte + cadáver que permanece
- Feedback visual: flash rojo al recibir daño
- Sin audio
- Solo cuerpo a cuerpo (enemigos y jugador)
- Velocidad media de movimiento
- Mapa 16x16
- Sin HUD de vida de enemigos
- Sin minimapa
- Desktop only

## Fase 1: Estructura base y rendering
### Tareas
- [ ] Crear archivo `index.html` con canvas a pantalla completa
- [ ] Implementar raycasting con LodeV
- [ ] Definir mapa del laberinto (grid 16x16)
- [ ] Renderizar vista en primera persona con columnas de rayos
- [ ] Implementar movimiento del jugador (WASD)

### Criterios aceptación
- Canvas renderiza paredes con efecto de profundidad
- Jugador puede moverse por el mapa sin atravesar paredes

## Fase 2: Enemigos y IA
### Tareas
- [ ] Representar enemigos como sprites 2D proyectados
- [ ] Implementar patrulla aleatoria de enemigos
- [ ] Sistema de detección: enemigos "ven" al jugador en cierto rango y ángulo
- [ ] Implementar estado `chase`: enemigo persigue al jugador
- [ ] Implementar `dying` state con animación de muerte (1 segundo)
- [ ] Implementar `dead` state con cadáver persistente

### Criterios aceptación
- 3 enemigos visibles en el mapa
- Enemigos patrullan cuando jugador no está en rango
- Enemigos persiguen al detectar jugador
- Al morir, enemigo muestra animación y deja cadáver

## Fase 3: Sistema de combate
### Tareas
- [ ] Implementar ataque con barra espaciadora
- [ ] Detectar si enemigo está en rango de golpe
- [ ] Aplicar daño a enemigo cercano (10 HP)
- [ ] Enemigos dañan al jugador cuando están en rango (10 HP)
- [ ] Cooldown de ataque (0.5s)
- [ ] Flash rojo en pantalla cuando jugador recibe daño

### Criterios aceptación
- Barra espaciadora reduce HP de enemigo cercano
- Enemigo que toca al jugador reduce su HP
- Flash rojo visible al recibir daño

## Fase 4: Estados de juego y UI
### Tareas
- [ ] Pantalla de menú inicial con botón Start
- [ ] Barra de vida del jugador en HUD
- [ ] Pantalla de victoria cuando todos los enemigos mueren
- [ ] Pantalla de derrota cuando HP jugador = 0
- [ ] Botón "Play Again" / "Volver al menú" en pantallas finales

### Criterios aceptación
- Flujo completo: menu -> playing -> victory/defeat -> menu
- HUD visible durante partida con barra de vida
- Pantallas de fin muestran el resultado correcto

## Fase 5: Polish y tests
### Tareas
- [ ] Añadir logging a `game.log`
- [ ] Tests E2E con Playwright
- [ ] Verificar que no hay errores en consola

## Mapa del laberinto (16x16)

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

### Raycasting (LodeV)
- Usar DDA (Digital Differential Analyzer)
- FOV: 60 grados
- Distancia máxima: 16 unidades

### Sprites de enemigos
- Proyectar posición 3D a 2D en pantalla
- Ordenar por distancia (painter's algorithm inverso)
- Escalar según distancia

### Detección de jugador por enemigo
- Rango de visión: 5 unidades
- Ángulo de visión: 90 grados (45° a cada lado)
- Line-of-sight bloqueada por paredes

### Velocidades
- Velocidad movimiento: 3 unidades/segundo
- Velocidad rotación: 2 radianes/segundo
- Velocidad ataque enemigo: 1 ataque/segundo
