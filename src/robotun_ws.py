import websocket
 
# WebSocket服务器的URL
ws_url = "ws://127.0.0.1:9001/agvLaserPinia/agvLaserPinia/agvLaserPinia"
 
# 创建一个WebSocket对象
ws = websocket.create_connection(ws_url)
 
# 发送一条消息到服务器
# ws.send("Hello, WebSocket!")
 
# 接收服务器的响应
response = ws.recv()
print("Received:", response)
 
# 关闭WebSocket连接
ws.close()