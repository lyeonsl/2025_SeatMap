import json
import asyncio
import websockets

# 클라이언트 1명이 연결되면 1분마다 좌석 상태를 계속 보내는 예시
async def send_status(websocket):
    while True:
        latest_status_json = {
            "timestamp": None,       # 초기엔 아직 추론 없음
            "total_seats": 30,
            "occupied": 0,
            "seats": [
                {"id": i, "occupied": False, "conf": 0.0} for i in range(1, 31)
            ],
        }
        await websocket.send(json.dumps(latest_status_json))
        await asyncio.sleep(60)  # 1분마다 전송

async def main():
    print("WebSocket 서버 listening: ws://0.0.0.0:8000")
    async with websockets.serve(send_status, "0.0.0.0", 8000):
        # 서버를 계속 유지
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

