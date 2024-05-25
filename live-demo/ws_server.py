#!/usr/bin/env python

import asyncio
import signal
import websockets

clients: set[websockets.WebSocketServerProtocol] = set()

async def handle(websocket: websockets.WebSocketServerProtocol):
    print(f"INFO: New connection from {websocket.remote_address}")
    if websocket.request_headers.get('Watering-Sensor-Client', '') == 'true':
        print(f"INFO: Sensor connected.")
        async for message in websocket:
            print(f"INFO: Sensor message: {message}, sending to {len(clients)} clients")
            await asyncio.gather(*[client.send(message) for client in clients])
    else:
        clients.add(websocket)
        try:
            async for message in websocket:
                print(f"WARN: Client message: {message}")
        finally:
            clients.remove(websocket)

async def server():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)

    async with websockets.serve(handle, "localhost", 8765):
        await stop

asyncio.run(server())
