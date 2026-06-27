# SeatMap 실시간 강의실 좌석 안내 서비스
실시간 강의실 좌석 안내 서비스

> YOLOv8 기반 딥러닝 모델과 스트리밍 서버를 활용하여 **강의실 좌석 점유 여부를 실시간 탐지**하고,  
> Flutter 앱에서 직관적으로 시각화하는 서비스입니다.  
> 학우들의 강의실 이용 편의를 높이고, 불필요한 냉방/조명 사용을 줄여 **에너지 절약**에도 기여하고자 개발하였습니다.

---

## 프로젝트 개요
- 강의실 좌석 점유 여부를 **실시간으로 탐지**  
- 사용자는 앱에서 좌석 배치도를 색상으로 직관적으로 확인    
- 학습 공간의 효율적 활용 + 캠퍼스 자원 최적화 달성  

---

## 핵심 기능
1. **실시간 좌석 탐지**  
   - YOLOv8 기반 객체 탐지 모델로 occupied / empty 분류  
2. **좌석 시각화**  
   - 앱 내에서 배치도를 색상(빨강/회색)으로 표현  
3. **원격 확인**  
   - 언제 어디서나 강의실 좌석 현황 확인 가능  

---

## 개발 프로세스
<p align="center">
  <img width="600" height="700" alt="image" src="https://github.com/user-attachments/assets/b10bf336-c963-47ec-b544-b24d572187f5" />
</p>

---

## 시스템 아키텍처
<p align="center">
  <img width="1280" height="720" alt="아키텍처" src="https://github.com/user-attachments/assets/2c5af9ab-407c-4a06-ac6c-e26443a75416" />
</p>

---

## 개발 환경
- **모델 학습**: ![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white) 
- **AI 프레임워크**: ![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logoColor=black) ![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)  
- **영상 처리**: ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)  
- **스트리밍**: ![Larix](https://img.shields.io/badge/Larix%20Broadcaster-FF4500?style=for-the-badge) ![MediaMTX](https://img.shields.io/badge/MediaMTX-228B22?style=for-the-badge)  
- **프론트엔드**: ![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
- **협업 툴**: ![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) 

---

## 실행 화면
<p align="center">
  <img width="115" height="255" alt="image" src="https://github.com/user-attachments/assets/0d8e114c-b21e-41cc-b368-8d59656b7143" />
   <img width="115" height="255" alt="image" src="https://github.com/user-attachments/assets/73f4eccf-1974-4ca6-94b0-2381d2e1b180" />
   <img width="115" height="255" alt="image" src="https://github.com/user-attachments/assets/fcb18d0d-95d9-48a9-8d70-9617aaffdc3f" />
</p>
<p align="center">
  <img width="115" height="255" alt="image" src="https://github.com/user-attachments/assets/732057c0-0a00-4341-a54d-96184d662f37" />
   <img width="115" height="255" alt="image" src="https://github.com/user-attachments/assets/757dc8b7-6677-442a-89b2-2ded48524c62" />
</p>

- **Home 화면**: 강의실 선택 → 실시간 좌석 배치도 확인  
- **Setting 화면**: 사용자 정보(이름, 학번, 학과) 수정  
- **좌석 표시**:  
  - 🔴 빨강 = 사람이 앉아 있거나 짐이 있는 좌석  
  - ⚪ 회색 = 빈 좌석  
- **메시지 알림**: 모든 좌석이 비어 있을 경우 “에어컨을 꺼주세요” 출력  

---

## 모델 성능
<p align="center">
  <img width="546" height="232" alt="image" src="https://github.com/user-attachments/assets/450d7d52-bf27-422b-b86b-eae94887dc88" />
</p>
<p align="center">
  <img width="488" height="62" alt="image" src="https://github.com/user-attachments/assets/a0ccf627-0e5d-4355-a909-8b5288617bae" />
</p>

- 약 **90% 정확도** 달성:contentReference[oaicite:1]{index=1}  
- 자체 데이터셋 + 외부 공개 데이터셋 병합 학습  
- 학습된 가중치(`best.pt`)를 실시간 추론에 적용  

---

## 향후 연구 방향
- **에너지 절감 연동 기능**: 무점유 상태가 일정 시간 지속되면 시설팀에 알림  
- **다강의실 확장**: 여러 강의실을 통합 관리하는 서버 아키텍처  
- **학사시스템 연동**: 강의실 예약/시간표와 점유 상태 비교  
- **다중 센서 활용**: 온도, 조도 센서와 추가 카메라로 정확도 향상  

---

## 레퍼런스
- 직접 구축한 데이터셋: [SeatMap Dataset](https://universe.roboflow.com/lyeonsl/seatmap-eeyuj)  
- 외부 공개 데이터셋: [Seat Detection](https://universe.roboflow.com/seat-detection/seat-detection-2zzxf)  
- 프로젝트 깃허브: [2025_SeatMap](https://github.com/YUM1yum/2025_SeatMap)  

---

## 팀 구성
- 팀명: **SM 모델공방**  
- 팀원: 이유민, 김연서, 김지연, 김주연, 박세희, 최서영
