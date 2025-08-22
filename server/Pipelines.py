# -*- coding: utf-8 -*-
# MediaMTX(RTSP) → ROI별 YOLO(best.pt) 추론 → 좌석별 점유/확신도 산출
# - seat_rois.json(선택): 정규화/픽셀 좌표, poly/rect 지원
# - table_anchors.json(선택): 테이블 n개 앵커 → 좌석 5개씩 자동 전개
# - 없으면 chair 검출로 부팅 시 좌석 자동 생성 → 마지막 폴백은 균일 그리드
# - 지속 추론(프레임 스킵), 디바운스, 주석화(옵션), WebSocket 1분 주기 푸시

import cv2
import time
import json
import asyncio
import threading
import websockets
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Any
import numpy as np
from ultralytics import YOLO

# ========= 설정 =========
RTSP_URL = "rtsp://172.20.13.56:8554/mystream?rtsp_transport=tcp"
MODEL_PATH = "best_seatmap_model.pt"          # ROI 단위 모델(occupied/empty 구분용)
IMG_SIZE = 640
CONF_THRES = 0.25
PUBLISH_INTERVAL_SEC = 60                     # 1분마다 푸시
SHOW_WINDOWS = True                           # 주석화 결과 화면 표시 여부
FRAME_SKIP = 2                                # 성능용. N-1 프레임은 건너뜀(0이면 매 프레임 추론)

# 폴백 그리드
ROWS, COLS = 5, 6

# '사람 있음'으로 간주할 클래스 이름(ROI 모델의 클래스 이름과 맞춰주세요)
OCCUPIED_CLASS_CANDIDATES = {"person", "occupied"}

# 디바운스(시간적 안정화)
ON_FRAMES = 3      # 최근 N프레임 중 히트 수 ≥ ON_FRAMES → occupied
OFF_FRAMES = 10    # 연속 미검출 ≥ OFF_FRAMES → empty

# ====== JSON 파일 경로 ======
SEAT_ROIS_JSON = "seat_rois.json"            # 좌석 ROI를 직접 지정(있으면 최우선)
TABLE_ANCHOR_JSON = "table_anchors.json"     # 테이블 앵커(있으면 좌석 5개씩 자동 생성)

# ====== 테이블 템플릿 & 자동좌석 옵션 ======
USE_TABLE_TEMPLATE = True     # table_anchors.json 있으면 사용
NUM_TABLES = 6
SEATS_PER_TABLE = 5
AUTO_SEATS = True             # 둘 다 없을 때 chair 검출로 좌석 자동 생성
BOOT_FRAMES = 60              # 부팅 시 의자 수집 프레임(≈2초)
CHAIR_MODEL = "yolov8n.pt"    # COCO 모델
CHAIR_CLASS_NAMES = {"chair"}
CHAIR_CONF = 0.30

# ====== ROI 일괄 보정(Affine-like) ======
CALIB_ENABLE = True
AX, BX = 1.00, 0.0            # x' = AX*x + BX
AY, BY = 0.93, -30            # y' = AY*y + BY   (예: 위로 30px, 세로 7% 축소)
# ========================


# ---------------------- 공통 유틸 ----------------------
def _xyxy_center(box):
    x1,y1,x2,y2 = box
    return (int((x1+x2)/2), int((y1+y2)/2))

def kmeans_centers(points, k, iters=15):
    """간단 KMeans (추가 의존성 없이)"""
    pts = np.array(points, dtype=np.float32)
    if len(pts) == 0: return np.empty((0,2), dtype=np.float32)
    if len(pts) <= k: return pts
    centers = pts[np.random.choice(len(pts), k, replace=False)]
    for _ in range(iters):
        d = ((pts[:,None,:]-centers[None,:,:])**2).sum(axis=2)
        idx = d.argmin(axis=1)
        newc = np.vstack([pts[idx==i].mean(axis=0) if np.any(idx==i) else centers[i] for i in range(k)])
        if np.allclose(newc, centers, atol=1e-2): break
        centers = newc
    return centers

def group_centers_to_tables(centers: List[Tuple[int,int]], num_tables=6):
    """좌석 중심들을 테이블 num_tables개로 군집화 → y(위→아래) 정렬"""
    if len(centers) == 0: return []
    pts = np.array(centers, dtype=np.float32)
    table_c = kmeans_centers(pts, k=num_tables)
    if len(table_c) == 0: return []
    d = ((pts[:,None,:]-table_c[None,:,:])**2).sum(axis=2)
    idx = d.argmin(axis=1)
    groups = {i: [] for i in range(len(table_c))}
    for p, gi in zip(centers, idx):
        groups[int(gi)].append(p)
    order = np.argsort(table_c[:,1])
    out = []
    for t_ord, gi in enumerate(order, start=1):
        members = groups[int(gi)]
        members = sorted(members, key=lambda c: (c[1], c[0]))  # y, x 정렬
        out.append((f"T{t_ord}", members))
    return out

def seat_boxes_from_centers(centers, box_w, box_h, img_w, img_h):
    boxes = []
    for (cx,cy) in centers:
        x1 = max(0, int(cx - box_w//2)); y1 = max(0, int(cy - box_h//2))
        x2 = min(img_w, int(cx + box_w//2)); y2 = min(img_h, int(cy + box_h//2))
        boxes.append((x1,y1,x2,y2))
    return boxes

def apply_calibration(polys_px, w, h):
    if not CALIB_ENABLE or len(polys_px) == 0: return polys_px
    def _adj(p):
        x = int(AX * p[0] + BX)
        y = int(AY * p[1] + BY)
        return (max(0, min(w-1, x)), max(0, min(h-1, y)))
    return [np.array([_adj(t) for t in poly], dtype=np.int32) for poly in polys_px]


# ---------------------- JSON 로더(좌석 ROI) ----------------------
def _to_px_poly_from_norm(poly_norm, h, w):
    return [(int(x*w), int(y*h)) for x, y in poly_norm]

def _to_px_rect_from_norm(rect_norm, h, w):
    x1, y1, x2, y2 = rect_norm
    return [(int(x1*w), int(y1*h)), (int(x2*w), int(y1*h)),
            (int(x2*w), int(y2*h)), (int(x1*w), int(y2*h))]

def _is_normalized_coords(coords):
    vals = []
    for p in coords:
        vals.extend(list(p))
        if len(vals) > 16: break
    vals = [abs(float(v)) for v in vals if v is not None]
    if not vals: return True
    small = sum(1 for v in vals if v <= 1.001)
    return small / len(vals) > 0.8

def load_seat_rois(h: int, w: int) -> Tuple[List[Dict[str, Any]], List[np.ndarray]]:
    p = Path(SEAT_ROIS_JSON)
    seats_meta, polys_px = [], []
    if not p.exists(): return [], []

    raw = json.loads(p.read_text(encoding="utf-8"))

    # 포맷 정규화
    if isinstance(raw, list):
        seats_iter = raw
    elif isinstance(raw, dict):
        seats_iter = raw.get("seats", [])
    else:
        raise ValueError("Unsupported JSON format for seats")

    # 정규화/절대 판단
    sample = []
    for it in seats_iter:
        if "poly" in it: sample.extend(it["poly"])
        elif "rect" in it:
            x1,y1,x2,y2 = it["rect"]; sample.extend([(x1,y1),(x2,y2)])
        if len(sample) > 12: break
    norm_like = _is_normalized_coords(sample)

    for it in seats_iter:
        sid = it.get("id")
        table = it.get("table", "T1")
        if "poly" in it:
            poly_px = _to_px_poly_from_norm(it["poly"], h, w) if norm_like \
                      else [(int(x), int(y)) for x,y in it["poly"]]
        elif "rect" in it:
            poly_px = _to_px_rect_from_norm(it["rect"], h, w) if norm_like \
                      else [(int(it["rect"][0]), int(it["rect"][1])),
                            (int(it["rect"][2]), int(it["rect"][1])),
                            (int(it["rect"][2]), int(it["rect"][3])),
                            (int(it["rect"][0]), int(it["rect"][3]))]
        else:
            continue
        poly_px = [(max(0,min(w-1,x)), max(0,min(h-1,y))) for (x,y) in poly_px]
        seats_meta.append({"id": sid, "table": table})
        polys_px.append(np.array(poly_px, dtype=np.int32))

    print(f"[ROI] Loaded {len(seats_meta)} seats from {SEAT_ROIS_JSON} "
          f"({ 'normalized' if norm_like else 'absolute px' })")
    return seats_meta, polys_px


# ---------------------- 테이블 앵커 로더 & 좌석 전개 ----------------------
def load_table_anchors(h, w):
    p = Path(TABLE_ANCHOR_JSON)
    if not (USE_TABLE_TEMPLATE and p.exists()): return []
    raw = json.loads(p.read_text(encoding="utf-8")).get("tables", [])
    anchors = []
    for t in raw:
        x1,y1,x2,y2 = t["rect"]
        if max(x1,x2,y1,y2) <= 1.001:  # 정규화
            x1,y1,x2,y2 = int(x1*w), int(y1*h), int(x2*w), int(y2*h)
        anchors.append((t["id"], (x1,y1,x2,y2)))
    return anchors

def expand_5_seats_from_table(table_rect):
    # 테이블 사각형 기준: 윗줄 3, 아랫줄 2
    x1,y1,x2,y2 = table_rect
    W, H = x2-x1, y2-y1
    pad_x, pad_y = int(W*0.10), int(H*0.12)
    cell_w, cell_h = int(W*0.22), int(H*0.34)

    seats = []
    xs_top = [x1+pad_x, x1+pad_x+cell_w+pad_x, x1+pad_x+(cell_w+pad_x)*2]
    for sx in xs_top:
        seats.append((sx, y1+pad_y, sx+cell_w, y1+pad_y+cell_h))
    xs_bot = [x1+pad_x+int(0.45*cell_w), x1+pad_x+int(1.45*cell_w)+pad_x]
    for sx in xs_bot:
        seats.append((sx, y1+pad_y+cell_h+pad_y, sx+cell_w, y1+pad_y+cell_h+pad_y+cell_h))
    return seats  # 5개


# ---------------------- 디바운스 트래커 ----------------------
class SeatTracker:
    def __init__(self, seats_meta: List[Dict[str, Any]]):
        self.ids = [s["id"] for s in seats_meta]
        self.state = {sid: "unknown" for sid in self.ids}
        self.counter_on = {sid: 0 for sid in self.ids}
        self.counter_off = {sid: 0 for sid in self.ids}
        self.conf = {sid: 0.0 for sid in self.ids}

    def update(self, hits: Dict[str, Tuple[bool, float]]):
        for sid in self.ids:
            occ, c = hits.get(sid, (False, 0.0))
            if occ:
                self.counter_on[sid] += 1
                self.counter_off[sid] = 0
                self.conf[sid] = max(self.conf[sid]*0.7, c)
                if self.state[sid] in ("unknown", "empty") and self.counter_on[sid] >= ON_FRAMES:
                    self.state[sid] = "occupied"
            else:
                self.counter_off[sid] += 1
                self.counter_on[sid] = 0
                self.conf[sid] = max(0.0, self.conf[sid]*0.5)
                if self.state[sid] in ("unknown", "occupied") and self.counter_off[sid] >= OFF_FRAMES:
                    self.state[sid] = "empty"

    def snapshot(self) -> Tuple[List[Dict[str, Any]], int]:
        seats_list, occ_count = [], 0
        for sid in self.ids:
            occ = (self.state[sid] == "occupied")
            if occ: occ_count += 1
            seats_list.append({"id": sid, "occupied": occ, "conf": round(float(self.conf[sid]), 3)})
        return seats_list, occ_count


# ---------------------- ROI 모델 ----------------------
model = YOLO(MODEL_PATH)

def infer_roi(crop_bgr) -> Tuple[bool, float]:
    res = model.predict(crop_bgr, imgsz=IMG_SIZE, conf=CONF_THRES, verbose=False)[0]
    occ_conf = 0.0
    if res.boxes is not None and len(res.boxes) > 0:
        cls = res.boxes.cls.cpu().numpy()
        conf = res.boxes.conf.cpu().numpy()
        for i in range(len(cls)):
            cls_name = model.names[int(cls[i])]
            if cls_name in OCCUPIED_CLASS_CANDIDATES:
                occ_conf = max(occ_conf, float(conf[i]))
    return (occ_conf > 0.0), occ_conf


# ---------------------- 전역 상태 ----------------------
latest_status_json = {"timestamp": None, "total_seats": 0, "occupied": 0, "seats": []}
latest_frame_annotated = None
latest_frame_lock = threading.Lock()

# RTSP
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
if not cap.isOpened():
    raise RuntimeError("RTSP 스트림 연결 실패. RTSP_URL 확인하세요.")


# ---------------------- 좌석 ROI 준비 ----------------------
def build_rois(h, w):
    seats_meta, polys_px = load_seat_rois(h, w)          # 1) 좌석 JSON
    if len(polys_px) > 0:
        return seats_meta, apply_calibration(polys_px, w, h)

    anchors = load_table_anchors(h, w)                    # 2) 테이블 앵커 → 좌석 템플릿
    if len(anchors) > 0:
        polys_px, seats_meta = _from_anchors(anchors, h, w)
        return seats_meta, apply_calibration(polys_px, w, h)

    if AUTO_SEATS:                                        # 3) 자동 좌석(의자 검출)
        centers = bootstrap_seats_by_chair(cap, frames=BOOT_FRAMES, k=NUM_TABLES*SEATS_PER_TABLE,
                                           chair_model_path=CHAIR_MODEL,
                                           chair_classes=CHAIR_CLASS_NAMES, conf=CHAIR_CONF)
        if centers:
            grouped = group_centers_to_tables(centers, num_tables=NUM_TABLES)
            box_w, box_h = int(0.05*w), int(0.08*h)
            seats_meta, polys_px = [], []
            for t_name, c_list in grouped:
                boxes = seat_boxes_from_centers(c_list, box_w, box_h, w, h)[:SEATS_PER_TABLE]
                for i,(x1,y1,x2,y2) in enumerate(boxes, start=1):
                    seats_meta.append({"id": f"{t_name}-S{i}", "table": t_name})
                    polys_px.append(np.array([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], dtype=np.int32))
            print(f"[AUTO] chairs→seats bootstrapped: {len(polys_px)}")
            return seats_meta, apply_calibration(polys_px, w, h)

    # 4) 마지막 폴백: 그리드
    seats_meta, polys_px = [], []
    cell_h, cell_w = h // ROWS, w // COLS
    for r in range(ROWS):
        tname = f"T{r+1}"
        for c in range(COLS):
            sid = f"S{r*COLS + c + 1}"
            x1, y1 = c * cell_w, r * cell_h
            x2, y2 = (c + 1) * cell_w, (r + 1) * cell_h
            polys_px.append(np.array([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], dtype=np.int32))
            seats_meta.append({"id": sid, "table": tname})
    print(f"[GRID] Using grid {ROWS}x{COLS} -> {len(seats_meta)} seats")
    return seats_meta, apply_calibration(polys_px, w, h)

def _from_anchors(anchors, h, w):
    polys_px, seats_meta = [], []
    for tname, rect in anchors:
        boxes = expand_5_seats_from_table(rect)
        for i,(x1,y1,x2,y2) in enumerate(boxes, start=1):
            seats_meta.append({"id": f"{tname}-S{i}", "table": tname})
            polys_px.append(np.array([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], dtype=np.int32))
    print(f"[TEMPLATE] built {len(polys_px)} seat ROIs from table anchors.")
    return polys_px, seats_meta


# ---------------------- Auto seats (의자 검출) ----------------------
def bootstrap_seats_by_chair(cap, frames=60, k=30, chair_model_path="yolov8n.pt",
                             chair_classes={"chair"}, conf=0.3):
    try:
        det = YOLO(chair_model_path)
    except Exception as e:
        print(f"[AUTO] load chair model failed: {e}")
        return []
    centers, grabbed = [], 0
    for _ in range(frames):
        ok, f = cap.read()
        if not ok: break
        grabbed += 1
        res = det.predict(f, imgsz=640, conf=conf, verbose=False)[0]
        if res.boxes is None or len(res.boxes) == 0: continue
        cls = res.boxes.cls.cpu().numpy()
        xyxy = res.boxes.xyxy.cpu().numpy().astype(int)
        for i in range(len(xyxy)):
            name = det.names[int(cls[i])]
            if name in chair_classes: centers.append(_xyxy_center(xyxy[i]))
    print(f"[AUTO] collected {len(centers)} chair centers from {grabbed} frames")
    if not centers: return []
    C = kmeans_centers(centers, k=int(k))
    return [tuple(map(int, c)) for c in C]


# ---------------------- 추론 루프 ----------------------
def inference_loop():
    global latest_status_json, latest_frame_annotated

    ok, frame = cap.read()
    if not ok: raise RuntimeError("초기 프레임 수신 실패")
    h, w = frame.shape[:2]

    seats_meta, polys_px = build_rois(h, w)
    tracker = SeatTracker(seats_meta)
    seat_ids = [s["id"] for s in seats_meta]
    total = len(seat_ids)

    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05); continue

        if FRAME_SKIP > 0 and (frame_index % (FRAME_SKIP + 1)) != 0:
            frame_index += 1; continue
        frame_index += 1

        hits = {}
        overlay = frame.copy()
        for sid, poly in zip(seat_ids, polys_px):
            x1 = int(np.min(poly[:, 0])); y1 = int(np.min(poly[:, 1]))
            x2 = int(np.max(poly[:, 0])); y2 = int(np.max(poly[:, 1]))
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 - x1 <= 2 or y2 - y1 <= 2:
                hits[sid] = (False, 0.0); continue
            crop = frame[y1:y2, x1:x2]
            occ, conf = infer_roi(crop)
            hits[sid] = (occ, conf)

        tracker.update(hits)
        seats_list, occ_count = tracker.snapshot()

        # 주석화
        for seat, poly in zip(seats_list, polys_px):
            color = (0, 0, 255) if seat["occupied"] else (80, 80, 80)
            cv2.polylines(overlay, [poly], True, color, 2)
            tx, ty = int(poly[0, 0]), int(poly[0, 1]) - 6
            cv2.putText(overlay, f"{seat['id']}|{'OCC' if seat['occupied'] else 'EMPTY'}|{seat['conf']:.2f}",
                        (tx, max(ty, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        with latest_frame_lock:
            latest_frame_annotated = overlay

        latest_status_json = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_seats": total,
            "occupied": occ_count,
            "seats": seats_list
        }
        time.sleep(0.005)


# ---------------------- 표시 루프 ----------------------
def show_loop():
    while True:
        with latest_frame_lock:
            vis = latest_frame_annotated.copy() if latest_frame_annotated is not None else None
        if vis is not None:
            cv2.imshow("Annotated Seats (YOLO ROI)", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        time.sleep(0.01)
    cv2.destroyAllWindows()


# ---------------------- WebSocket ----------------------
connected = set()
async def ws_handler(websocket, *args):
    connected.add(websocket)
    try:
        await websocket.send(json.dumps(latest_status_json or {}))
        while True:
            await websocket.send(json.dumps(latest_status_json or {}))
            await asyncio.sleep(PUBLISH_INTERVAL_SEC)
    finally:
        connected.discard(websocket)

def run_ws_server():
    print("WebSocket: ws://0.0.0.0:8765 (좌석 상태 1분 주기 푸시)")
    async def _serve():
        async with websockets.serve(ws_handler, "0.0.0.0", 8765, ping_interval=None, ping_timeout=None):
            await asyncio.Future()
    asyncio.run(_serve())


# ---------------------- main ----------------------
if __name__ == "__main__":
    threading.Thread(target=inference_loop, daemon=True).start()
    threading.Thread(target=run_ws_server, daemon=True).start()
    if SHOW_WINDOWS:
        show_loop()
    else:
        while True: time.sleep(60)