# Consola de Comandos - WebDoom

## Acceso a la Consola

Presiona **ALT+P** para abrir la consola.
Presiona **ALT+P** nuevamente para cerrar la consola.

Cuando la consola está abierta:
- Los controles del juego están desactivados
- El juego se pausa
- Puedes escribir comandos y presionar **ENTER** para ejecutarlos

## Comandos Disponibles

### help
Muestra la lista de comandos disponibles.

```
help
```

### status
Muestra el estado actual del juego:
- Estado del juego (menu, playing, victory, defeat)
- Posición y estado del jugador
- Número de enemigos
- Estado de pausa
- Estado de la consola

```
status
```

### heal
Cura al jugador completamente (100 HP).

```
heal
```

### kill
Elimina a todos los enemigos actuales.

```
kill
```

### spawn
Spawnear un enemigo en una posición específica.

```
spawn <x> <y>
```

Ejemplo:
```
spawn 5.5 5.5
```

### god
Alternar modo dios (invencibilidad del jugador).

```
god
```

### speed
Establecer multiplicador de velocidad de movimiento.

```
speed <n>
```

Donde `n` es un número entre 1 y 10.
- `speed 1` = velocidad normal
- `speed 5` = 5x velocidad
- `speed 10` = 10x velocidad

Ejemplo:
```
speed 3
```

### clear
Limpiar la consola (borrar todo el texto).

```
clear
```

## Controles del Juego

| Tecla | Acción |
|-------|--------|
| W | Movimiento hacia adelante |
| S | Movimiento hacia atrás |
| A | Strafe izquierdo |
| D | Strafe derecho |
| Flecha Izquierda | Rotar cámara izquierda |
| Flecha Derecha | Rotar cámara derecha |
| Espacio | Atacar (golpe cuerpo a cuerpo) |
| ESC | Pausar juego / Volver al menú |
| ALT+P | Abrir/Cerrar consola |

## Menú de Pausa

Cuando presionas **ESC** durante el juego:
- El juego se pausa
- Aparece el menú de pausa con opciones:
  - **REANUDAR** - Continuar el juego desde el punto donde se pausó
  - **MENÚ PRINCIPAL** - Volver al menú principal

## Botón COMENZAR

- Si estás en el **menú principal**: Inicia una nueva partida desde el principio
- Si estás en **pausa**: Reanuda el juego desde donde lo dejaste
