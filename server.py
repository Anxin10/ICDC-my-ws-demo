import asyncio
import websockets
import json
import os   # 新增這行

connected_clients = set()
latest_control_data = None

async def handler(websocket):
    global latest_control_data
    print(f"[+] Client connected")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if "ctrl" in data:
                    latest_control_data = data["ctrl"]
                    print(f"[ESP32] Input: {latest_control_data}")
                    for client in connected_clients:
                        if client != websocket:
                            await client.send(json.dumps({"ctrl": latest_control_data}))
            except Exception as e:
                print("Invalid JSON or error:", e)
    except websockets.exceptions.ConnectionClosed:
        print("[-] Client disconnected")
    finally:
        connected_clients.remove(websocket)

async def main():
    PORT = int(os.environ.get("PORT", 8765))  # 改這行
    print(f"Starting WebSocket server on ws://0.0.0.0:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):   # 改這行
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
