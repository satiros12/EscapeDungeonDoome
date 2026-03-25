# WebDoom

FPS estilo DOOM con arquitectura cliente-servidor.

## Requisitos

- Python 3.8+
- Node.js (para tests)
- Navegador moderno

## Instalación

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node
npm install
```

## Cómo Ejecutar

```bash
# Puerto por defecto (8000/8001)
./start.sh

# Puerto personalizado
python3 src/server/server.py --host 0.0.0.0 --port 5000 --ws-port 5001
```

Luego abre `http://localhost:8000` en tu navegador.

## Controles

| Tecla | Acción |
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

## Consola

Presiona `ALT+P` para abrir la consola. Comandos:
- `help` - Ver comandos
- `heal` - Curar jugador
- `kill` - Matar enemigos
- `god` - Modo dios
- `spawn <x> <y>` - Crear enemigo
- `speed <n>` - Velocidad (1-10)

## Tests

```bash
# Tests E2E (Playwright)
npm test
```

## Estructura

```
public/          # Frontend (HTML+JS)
src/server/      # Backend (Python)
tests/e2e/       # Tests E2E
docs/            # Documentación
```