import cv2
import torch
import pathlib
import math
pathlib.PosixPath = pathlib.WindowsPath 

YOLO_DIR = "C:/Users/odu39/capstone/yolov5"
# YOLOv5 경로 설정
yolov5_path = pathlib.Path(YOLO_DIR)  # YOLOv5가 설치된 경로로 변경해야 합니다.

# YOLOv5 모델 로드
model = torch.hub.load(str(yolov5_path), "custom", "best.pt", source="local", verbose=False, force_reload=True)
model.eval()

# 웹캠에서 프레임 읽기
cap = cv2.VideoCapture(0)
half_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
half_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
print(half_width, half_height)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    # # YOLOv5를 위한 입력 전처리
    # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # img = model.preprocess(img)[0]

    # # 추론
    # with torch.no_grad():
    #     results = model(img)

    # 중심 좌표값 표시
    for result in results.pred:
        for box in result[:, :4]:
            x_center = int((box[0] + box[2]) / 2)
            y_center = int((box[1] + box[3]) / 2)
            box_width = int(box[2] - box[0])
            box_heigt = int(box[3] - box[1])
            cv2.circle(frame, (x_center, y_center), 5, (0, 255, 0), -1)
            diag = math.sqrt((x_center - half_width)**2 + (y_center - half_height)**2)
            cv2.putText(frame, f'({int(((x_center - half_width)/diag)*100)}, {int(((y_center - half_height)/diag)*100)}, {int(diag)}, {box_width*box_heigt})', (x_center, y_center), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_8, False)


    # 화면에 프레임 표시
    cv2.imshow("YOLOv5 Object Detection", frame)

    # 종료 키 확인
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 종료
cap.release()
cv2.destroyAllWindows()
