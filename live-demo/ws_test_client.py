import asyncio
import websockets

async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        async for message in websocket:
            print(f"INFO: Received message: {message}")

asyncio.run(main())
