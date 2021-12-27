import asyncio
import websockets
from ancillary_service import process_data_packets


async def data_stream_handler(websocket):
    """Receive the message and schedule it for processing."""
    while True:
        try:
            message = await websocket.recv()
            process_data_packets.apply_async(args=[message], queue="pg")
        except websockets.ConnectionClosedOK:
            break


async def main():
    async with websockets.serve(data_stream_handler, "127.0.0.1", 8000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
