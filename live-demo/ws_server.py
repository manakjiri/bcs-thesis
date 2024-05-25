#!/usr/bin/env python

import asyncio
import signal
import websockets
import ssl

class Handler:
    def __init__(self) -> None:
        self.clients: set[websockets.WebSocketServerProtocol] = set()
        self.last_message = ''

    async def handle(self, websocket: websockets.WebSocketServerProtocol):
        print(f"INFO: New connection from {websocket.remote_address}")
        try:
            if websocket.request_headers.get('watering-sensor-client', '') == 'true':
                print(f"INFO: Sensor connected.")
                async for message in websocket:
                    print(f"INFO: Sensor message: {message}, sending to {len(self.clients)} clients")
                    self.last_message = message
                    await asyncio.gather(*[client.send(message) for client in self.clients])
            else:
                self.clients.add(websocket)
                try:
                    if self.last_message:
                        await websocket.send(self.last_message)
                    async for message in websocket:
                        print(f"WARN: Client message: {message}")
                finally:
                    self.clients.remove(websocket)
        except:
            print(f"ERROR: Connection lost from {websocket.remote_address}")

async def server():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain("cert.pem", "cert.pem")

    handler = Handler()
    async with websockets.serve(handler.handle, "0.0.0.0", 8765, ssl=ssl_context):
        await stop

asyncio.run(server())
