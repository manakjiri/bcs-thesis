import asyncio
import websockets

async def main():
    async with websockets.connect("wss://new-horizons.lumias.cz:8765") as websocket:
        async for message in websocket:
            print(f"INFO: Received message: {message}")

asyncio.run(main())
