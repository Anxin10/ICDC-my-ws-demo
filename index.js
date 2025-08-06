const WebSocket = require('ws');
const http = require('http');

const port = process.env.PORT || 3000;

// 建立 HTTP server
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end("WebSocket server is running");
});

// 用 HTTP server 建立 WebSocket
const wss = new WebSocket.Server({ server });

wss.on('connection', ws => {
  console.log('🟢 客戶端已連線');

  ws.on('message', message => {
    console.log('📨 收到訊息:', message);
    ws.send(`你說了：${message}`);
  });

  ws.on('close', () => {
    console.log('🔴 客戶端離線');
  });
});

server.listen(port, () => {
  console.log(`✅ 伺服器運作中（port: ${port}）`);
});
