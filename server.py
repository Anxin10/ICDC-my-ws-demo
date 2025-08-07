from aiohttp import web
import os
import json

connected_clients = set()
latest_control_data = None

async def websocket_handler(request):
    global latest_control_data
    ws = web.WebSocketResponse()  # 允許 arduino 子協議
    await ws.prepare(request)

    print(f"[+] Client connected")
    connected_clients.add(ws)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    if "ctrl" in data:
                        latest_control_data = data["ctrl"]
                        print(f"[Client] Input: {latest_control_data}")
                        for client in connected_clients:
                            if client != ws:
                                await client.send_json({"ctrl": latest_control_data})
                except Exception as e:
                    print("Invalid JSON or error:", e)
    finally:
        connected_clients.remove(ws)
        print("[-] Client disconnected")

    return ws

async def index(request):
    return web.Response(text="WebSocket server is running.")

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)

PORT = int(os.environ.get("PORT", 8080))
web.run_app(app, port=PORT)


