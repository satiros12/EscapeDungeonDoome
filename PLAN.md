# PLAN.md - WebDoom MVP

## Resumen requisitos
- Colores sólidos simples
- Animación de muerte + cadáver que permanece
- Feedback visual: flash rojo al recibir daño, HIT! al golpear
- Sin audio
- Solo cuerpo a cuerpo (enemigos y jugador)
- Velocidad media de movimiento
- Mapa 16x16 arena abierta
- Sin HUD de vida de enemigos
- Sin minimapa
- Desktop only

## Fase 1: Estructura base y rendering - COMPLETA
- [x] Crear archivo `index.html` con canvas a pantalla completa
- [x] Implementar raycasting
- [x] Definir mapa del laberinto (grid 16x16)
- [x] Renderizar vista en primera persona con columnas de rayos
- [x] Implementar movimiento del jugador (WASD)

## Fase 2: Enemigos y IA - COMPLETA
- [x] Representar enemigos como sprites 2D proyectados
- [x] Implementar patrulla aleatoria de enemigos
- [x] Sistema de detección con line-of-sight
- [x] Implementar estado `chase`: enemigo persigue al jugador
- [x] Implementar `dying` state con animación de muerte
- [x] Implementar `dead` state con cadáver persistente

## Fase 3: Sistema de combate - COMPLETO
- [x] Implementar ataque con barra espaciadora
- [x] Detectar si enemigo está en rango de golpe
- [x] Aplicar daño a enemigo cercano (10 HP)
- [x] Enemigos dañan al jugador cuando están en rango (10 HP)
- [x] Cooldown de ataque (0.5s)
- [x] Flash rojo en pantalla cuando jugador recibe daño
- [x] Efecto visual "HIT!" al golpear enemigo

## Fase 4: Estados de juego y UI - COMPLETO
- [x] Pantalla de menú inicial con botón Start
- [x] Barra de vida del jugador en HUD
- [x] Contador de kills (X/3)
- [x] Pantalla de victoria cuando todos los enemigos mueren
- [x] Pantalla de derrota cuando HP jugador = 0
- [x] Botón "Volver al menú" en pantallas finales

## Fase 5: Polish y tests - COMPLETO
- [x] Logging a `game.log` desde servidor Python
- [x] Tests E2E con Playwright (10 tests)
- [x] Sin errores en consola

## Mapa actual (arena abierta)

```
################
#              #
#   E          #
#              #
#      P       #
#          E   #
#              #
#              #
#              #
#              #
#              #
#              #
#          E   #
#              #
#              #
################
```

## Detalles técnicos

### Raycasting
- DDA (Digital Differential Analyzer)
- FOV: 60 grados
- Distancia máxima: 16 unidades

### Sprites de enemigos
- Proyección 3D a 2D
- Orden por distancia (painter's algorithm inverso)
- Escala según distancia

### Detección de enemigo
- Rango de visión: 5 unidades
- Ángulo de visión: 90 grados
- Line-of-sight bloqueada por paredes

### Velocidades
- Movimiento: 3 unidades/segundo
- Rotación: 2 radianes/segundo
- Ataque enemigo: 1 ataque/segundo
- Ataque jugador: cooldown 0.5s
