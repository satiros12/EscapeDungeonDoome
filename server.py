#!/usr/bin/env python3
"""WebDoom MVP - HTTP + WebSocket Server with Game Loop"""

import asyncio
import argparse
import http.server
import socketserver
import os
import json
import threading
from datetime import datetime
import websockets
from game_state import GameState, GameConfig
from game_logic import GameLogic

LOG_FILE = "game.log"


class LogHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_POST(self):
        if self.path == "/log":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
                entry = f"[{data['time']}] {data['msg']}\n"
                with open(LOG_FILE, "a") as f:
                    f.write(entry)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class GameServer:
    def __init__(self, host="0.0.0.0", http_port=8000, ws_port=8001):
        self.host = host
        self.http_port = http_port
        self.ws_port = ws_port
        self.state = GameState()
        self.logic = GameLogic(self.state)
        self.clients = set()
        self.running = False

        def server_log(msg, level="INFO"):
            entry = f"[{datetime.now().isoformat()}] [{level}] {msg}\n"
            with open(LOG_FILE, "a") as f:
                f.write(entry)
            print(f"[{level}] {msg}")

        self.logic.set_logger(server_log)

    async def handle_client(self, websocket, path=""):
        """Handle individual client WebSocket connection"""
        print(f"DEBUG: handle_client called with path={path}")
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

        try:
            async for message in websocket:
                print(f"Received message: {repr(message)[:100]}")
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    print(f"Message type: {msg_type}")

                    if msg_type == "input":
                        print(f"DEBUG: Processing input message")
                        self.state.pending_input = data.get("keys", {})

                    elif msg_type == "start":
                        print(f"DEBUG: Processing START message", flush=True)
                        print(
                            f"DEBUG: Before reset - game_state = {self.state.game_state}",
                            flush=True,
                        )
                        self.state.reset()
                        print(
                            f"DEBUG: After reset - game_state = {self.state.game_state}",
                            flush=True,
                        )
                        self.state.game_state = "playing"
                        print(
                            f"DEBUG: After setting playing - game_state = {self.state.game_state}",
                            flush=True,
                        )
                        self.logic.log("Game started by client")

                    elif msg_type == "attack":
                        self.logic.player_attack()

                    elif msg_type == "resume":
                        print(f"DEBUG: Processing RESUME message", flush=True)
                        self.state.game_state = "playing"
                        self.logic.log("Game resumed by client")

                    elif msg_type == "menu":
                        print(f"DEBUG: Processing MENU message", flush=True)
                        self.state.game_state = "menu"
                        self.logic.log("Returned to menu")

                    elif msg_type == "console_command":
                        cmd = data.get("command", "")
                        if cmd == "kill_all":
                            for enemy in self.state.enemies:
                                enemy.health = 0
                                enemy.state = "dead"
                                self.state.corpses.append(Corpse(x=enemy.x, y=enemy.y))
                                self.state.kills += 1
                        elif cmd == "god":
                            self.state.player.god_mode = not getattr(
                                self.state.player, "god_mode", False
                            )
                        elif cmd == "speed":
                            speed = data.get("value", 1)
                            self.state.player_speed_multiplier = speed

                    elif msg_type == "get_state":
                        await websocket.send(json.dumps(self.state.to_dict()))

                    else:
                        print(f"Unknown message type: {msg_type}")

                except json.JSONDecodeError:
                    print("Invalid JSON received")
                except Exception as e:
                    import traceback

                    print(f"Error processing message: {e}")
                    traceback.print_exc()

        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_state(self):
        """Broadcast game state to all connected clients"""
        print(f"DEBUG broadcast_state: clients count = {len(self.clients)}")
        if not self.clients:
            return

        message = json.dumps(self.state.to_dict())

        await asyncio.gather(
            *[ws.send(message) for ws in self.clients], return_exceptions=True
        )

    async def game_loop(self):
        """Main game loop at 60 FPS"""
        FPS = 60
        dt = 1.0 / FPS

        print(f"Game loop started at {FPS} FPS")

        while self.running:
            try:
                if self.state.game_state == "playing":
                    self.logic.update(dt)

                await self.broadcast_state()
                await asyncio.sleep(dt)

            except Exception as e:
                print(f"Game loop error: {e}")

    async def ws_handler(self, websocket):
        """WebSocket connection handler"""
        print(f"DEBUG ws_handler: got websocket {id(websocket)}")
        try:
            await self.handle_client(websocket)
        except Exception as e:
            print(f"DEBUG ws_handler error: {e}")

    async def start_ws_server(self):
        """Start WebSocket server"""
        async with websockets.serve(self.ws_handler, self.host, self.ws_port):
            print(f"WebSocket server running on ws://{self.host}:{self.ws_port}")
            await asyncio.Future()

    def run(self):
        """Run both HTTP and WebSocket servers"""
        self.running = True

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        http_thread = threading.Thread(target=self.run_http_server)
        http_thread.daemon = True
        http_thread.start()

        print(f"HTTP server running at http://{self.host}:{self.http_port}", flush=True)

        async def run_server():
            ws_server = await websockets.serve(self.ws_handler, self.host, self.ws_port)
            print(
                f"WebSocket server running on ws://{self.host}:{self.ws_port}",
                flush=True,
            )
            print(f"Game loop running at 60 FPS", flush=True)

            while self.running:
                if self.state.game_state == "playing":
                    dt = 1.0 / 60
                    self.logic.update(dt)

                await self.broadcast_state()
                await asyncio.sleep(1 / 60)

            ws_server.close()
            await ws_server.wait_closed()

        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False
            loop.close()

    def run_http_server(self):
        """Run HTTP server in separate thread"""
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer((self.host, self.http_port), LogHandler) as httpd:
            httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="WebDoom Server")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="HTTP port (default: 8000)"
    )
    parser.add_argument(
        "--ws-port", type=int, default=8001, help="WebSocket port (default: 8001)"
    )
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with open(LOG_FILE, "w") as f:
        f.write(f"[{datetime.now().isoformat()}] Server started\n")

    print("=" * 50)
    print("WebDoom Server")
    print("=" * 50)
    print(f"HTTP:      http://{args.host}:{args.port}")
    print(f"WebSocket: ws://{args.host}:{args.ws_port}")
    print("=" * 50)

    server = GameServer(args.host, args.port, args.ws_port)
    server.run()


if __name__ == "__main__":
    main()
