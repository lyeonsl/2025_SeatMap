# yolo_rtsp_to_ws.py
import os, json, time, threading
import cv2
from shapely.geometry import Point, Polygon
from ultralytics import YOLO
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# ---------- 1) 설정 ----------
RTSP = os.getenv("RTSP_518", "rtsp://172.20.37.206:8554/live/cam1")  # ← PC_IP 입력
MODEL = "best_seatmap_model.pt"                                 # ← 첨부한 모델
ROI_JSON = "seat_rois_518.json"                                  # ← 생성한 ROI 파일
IMG_SIZE = 960            # 추론 해상도(성능/지연 균형)
CONF_THR = 0.5
IOU_THR  = 0.5
RISE, DECAY = 2, 2        # 히스테리시스(깜빡임 완화)

# ---------- 2) 로드 ----------
app = FastAPI()
model = YOLO(MODEL)         # GPU 있으면 model.to("cuda")
with open(ROI_JSON, "r", encoding="utf-8") as f:
    roi = json.load(f)
SEAT_POLYS = { s["id"]: Polygon(s["poly"]) for s in roi["seats"] }
latest_status = { sid: False for sid in SEAT_POLYS }
confirm_buf   = { sid: 0     for sid in SEAT_POLYS }
subscribers = set()

# ---------- 3) 좌석 판정 ----------
def assign_to_seats(dets):
    """
    dets: [(x1,y1,x2,y2,conf,cls), ...]  (cls=0: person 가정)
    바닥 중앙점(cx, y2)이 어떤 좌석 폴리곤에 들어가는지로 점유 판정
    """
    occ = { sid: False for sid in SEAT_POLYS }
    for (x1, y1, x2, y2, conf, cls) in dets:
        cx = (x1 + x2) / 2.0
        cy = y2
        p = Point(cx, cy)
        for sid, poly in SEAT_POLYS.items():
            if poly.contains(p):
                occ[sid] = True
    return occ

def smooth_update(new_occ):
    changed = False
    for sid, occ in new_occ.items():
        if occ:
            confirm_buf[sid] = min(confirm_buf[sid] + 1, RISE)
            if confirm_buf[sid] >= RISE and latest_status[sid] is False:
                latest_status[sid] = True; changed = True
        else:
            confirm_buf[sid] = max(confirm_buf[sid] - 1, -DECAY)
            if confirm_buf[sid] <= -DECAY and latest_status[sid] is True:
                latest_status[sid] = False; changed = True
    return changed

# ---------- 4) 추론 스레드 ----------
def inference_loop():
    cap = cv2.VideoCapture(RTSP, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        raise RuntimeError("RTSP 열기 실패: URL/방화벽/MediaMTX 상태 확인")

    last_emit = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1); continue

        results = model.predict(frame, imgsz=IMG_SIZE, conf=CONF_THR, iou=IOU_THR, verbose=False)
        dets = []
        for r in results:
            if r.boxes is None: 
                continue
            for b in r.boxes:
                cls = int(b.cls[0].item())
                if cls != 0:  # 사람 클래스만
                    continue
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                conf = float(b.conf[0].item())
                dets.append((x1,y1,x2,y2,conf,cls))

        if smooth_update(assign_to_seats(dets)):
            payload = json.dumps({"room": "518", "ts": time.time(), "seats": latest_status})
            broadcast(payload)
        else:
            # 하트비트(선택)
            if time.time() - last_emit > 1.0:
                payload = json.dumps({"room": "518", "ts": time.time(), "seats": latest_status})
                broadcast(payload)
                last_emit = time.time()

def broadcast(payload: str):
    # 간단 브로드캐스트 (에러처리는 최소)
    dead = []
    for ws in list(subscribers):
        try:
            import anyio
            anyio.from_thread.run(ws.send_text, payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        try: subscribers.remove(ws)
        except: pass

# ---------- 5) FastAPI 엔드포인트 ----------
@app.on_event("startup")
def start_worker():
    t = threading.Thread(target=inference_loop, daemon=True)
    t.start()

@app.get("/health")
def health():
    return {"ok": True, "room": "518"}

@app.websocket("/ws/518")
async def ws_518(websocket: WebSocket):
    await websocket.accept()
    subscribers.add(websocket)
    try:
        # 최초 상태 즉시 전송
        await websocket.send_json({"room": "518", "ts": time.time(), "seats": latest_status})
        while True:
            await websocket.receive_text()  # 핑/더미 수신
    except WebSocketDisconnect:
        try: subscribers.remove(websocket)
        except: pass
