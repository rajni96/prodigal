import asyncio
import websockets
import json
import time


async def send_data_packets():
    """Reads the json from the file and send it to the websocket server."""
    async with websockets.connect("ws://localhost:8000") as websocket:
        f = open("data_packets.json")
        data_packets = json.load(f)
        for packet in data_packets:
            await websocket.send(json.dumps(packet))
        # Closing file
        f.close()


asyncio.run(send_data_packets())
