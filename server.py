from aiohttp import web
import os
import json

# 用於儲存所有已連線的客戶端
connected_clients = set()
# 用於儲存最新的控制指令
latest_control_data = None

# WebSocket 的主要處理邏輯
async def websocket_handler(request):
    global latest_control_data
    
    # 建立一個 WebSocket 回應物件
    ws = web.WebSocketResponse()
    # 準備處理 WebSocket 請求 (完成交握)
    await ws.prepare(request)

    print(f"[+] 客戶端已連線: {request.remote}")
    connected_clients.add(ws)

    try:
        # 非同步地監聽來自此客戶端的訊息
        async for msg in ws:
            # 確認訊息類型是文字
            if msg.type == web.WSMsgType.TEXT:
                try:
                    # 解析 JSON 字串
                    data = json.loads(msg.data)
                    # 如果訊息中包含 'ctrl' 鍵，代表是 ESP32 送來的控制指令
                    if "ctrl" in data:
                        latest_control_data = data["ctrl"]
                        print(f"[ESP32] 收到指令: {latest_control_data}")
                        
                        # 廣播此指令給所有其他已連線的客戶端
                        for client in connected_clients:
                            if client != ws and not client.closed:
                                await client.send_json({"ctrl": latest_control_data})
                except json.JSONDecodeError:
                    print(f"[警告] 收到了無效的 JSON 格式訊息: {msg.data}")
                except Exception as e:
                    print(f"[錯誤] 處理訊息時發生錯誤: {e}")
            # 如果收到關閉訊息，就中斷迴圈
            elif msg.type == web.WSMsgType.ERROR:
                print(f"[錯誤] 連線發生錯誤: {ws.exception()}")
    except Exception as e:
        print(f"[-] 客戶端連線處理時發生未預期錯誤: {e}")
    finally:
        # 當連線中斷或發生錯誤時，將客戶端從集合中移除
        connected_clients.remove(ws)
        print(f"[-] 客戶端已離線: {request.remote}")

    return ws

# 用於處理根路徑 '/' 的一般 HTTP 請求
async def index(request):
    return web.Response(text="WebSocket server is running with aiohttp.")

# 建立 aiohttp 應用程式
app = web.Application()

# 設定路由
app.router.add_get("/", index)         # 處理一般網頁請求
app.router.add_get("/ws", websocket_handler) # 處理 WebSocket 連線請求

if __name__ == "__main__":
    # 從環境變數取得 PORT，若無則預設為 8080
    PORT = int(os.environ.get("PORT", 8080))
    print(f"伺服器啟動於 http://0.0.0.0:{PORT}")
    # 執行應用程式
    web.run_app(app, port=PORT)
