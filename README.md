# 2025_SeatMap 실시간 강의실 좌석 안내 서비스
2025_Engineering Academic Competition

> YOLOv8 기반 딥러닝 모델과 스트리밍 서버를 활용하여 **강의실 좌석 점유 여부를 실시간 탐지**하고,  
> Flutter 앱에서 직관적으로 시각화하는 서비스입니다.  
> 학우들의 강의실 이용 편의를 높이고, 불필요한 냉방/조명 사용을 줄여 **에너지 절약**에도 기여하고자 개발하였습니다.

---

## 🚀 프로젝트 개요
- 강의실 좌석 점유 여부를 **실시간으로 탐지**  
- 사용자는 앱에서 좌석 배치도를 색상으로 직관적으로 확인    
- 학습 공간의 효율적 활용 + 캠퍼스 자원 최적화 달성  

---

## 🔑 핵심 기능
1. **실시간 좌석 탐지**  
   - YOLOv8 기반 객체 탐지 모델로 occupied / empty 분류  
2. **좌석 시각화**  
   - 앱 내에서 배치도를 색상(빨강/회색)으로 표현  
3. **원격 확인**  
   - 언제 어디서나 강의실 좌석 현황 확인 가능  

---

## 🛠️ 시스템 아키텍처

![Architecture](./docs/classroom_seat_service_architecture_icons.png)

### 전체 파이프라인
1. **Larix Broadcaster**  
   - 모바일 기기에서 RTSP 스트림 송출  
2. **MediaMTX**  
   - RTSP 스트림 수신 및 전달  
3. **OpenCV**  
   - 프레임 추출, ROI(좌석 영역) 전처리  
4. **YOLOv8**  
   - occupied / empty 상태 추론  
5. **JSON**  
   - 좌석별 상태 정리  
6. **WebSocket 서버**  
   - 실시간으로 결과 전송  
7. **Flutter 앱**  
   - 좌석 색상(빨강/회색) 표시 + 에어컨 OFF 메시지  

---

## 📂 개발 환경
- **모델 학습**: Google Colab, Jupyter Notebook  
- **AI 프레임워크**: YOLOv8 (Ultralytics), PyTorch, TensorFlow  
- **영상 처리**: OpenCV  
- **스트리밍**: Larix Broadcaster, MediaMTX  
- **프론트엔드**: Flutter (WebSocket 기반 실시간 반영)  
- **협업 툴**: Notion, GitHub, Discord, Figma  

---

## 🖼️ 실행 화면
- **Home 화면**: 강의실 선택 → 실시간 좌석 배치도 확인  
- **Setting 화면**: 사용자 정보(이름, 학번, 학과) 수정  
- **좌석 표시**:  
  - 🔴 빨강 = 사람이 앉아 있거나 짐이 있는 좌석  
  - ⚪ 회색 = 빈 좌석  
- **메시지 알림**: 모든 좌석이 비어 있을 경우 “에어컨을 꺼주세요” 출력  

---

## 📊 모델 성능
- 약 **90% 정확도** 달성:contentReference[oaicite:1]{index=1}  
- 자체 데이터셋 + 외부 공개 데이터셋 병합 학습  
- 학습된 가중치(`best.pt`)를 실시간 추론에 적용  

---

## 🔮 향후 연구 방향
- **에너지 절감 연동 기능**: 무점유 상태가 일정 시간 지속되면 시설팀에 알림  
- **다강의실 확장**: 여러 강의실을 통합 관리하는 서버 아키텍처  
- **학사시스템 연동**: 강의실 예약/시간표와 점유 상태 비교  
- **다중 센서 활용**: 온도, 조도 센서와 추가 카메라로 정확도 향상  

---

## 📌 레퍼런스
- 직접 구축한 데이터셋: [SeatMap Dataset](https://universe.roboflow.com/lyeonsl/seatmap-eeyuj)  
- 외부 공개 데이터셋: [Seat Detection](https://universe.roboflow.com/seat-detection/seat-detection-2zzxf)  
- 프로젝트 깃허브: [2025_SeatMap](https://github.com/YUM1yum/2025_SeatMap)  

---

## 👨‍💻 팀 구성
- 팀명: **SM 모델공방**  
- 팀원: 이유민, 김연서, 김지연, 김주연, 박세희, 최서영
