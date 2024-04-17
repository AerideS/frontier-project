import cv2
import torch
import pathlib
import math
import asyncio

# 윈도우 환경에서 작동할 때 사용
# pathlib.PosixPath = pathlib.WindowsPath  # only for windows


class FindTree:
    def __init__(self) -> None:
        '''
        초기화 과정, 
        '''
        pass
    
    async def find_tree_coordinate(self):
        '''
        작동 과정
        카메라 읽기 -> 이미지 객체 판독 -> 박스 결과 yield로 반환하기 반복
        '''
        pass
    
# YOLO_DIR = "C:/Users/HA/Downloads/yolov5-master"
YOLO_DIR = './' # 현재 경로
# YOLOv5 경로 설정
yolov5_path = pathlib.Path(YOLO_DIR)  # YOLOv5가 설치된 경로로 변경해야 합니다.

# YOLOv5 모델 로드
model = torch.hub.load(str(yolov5_path), "custom", "best.pt", source="local", verbose=False, force_reload=True)
model.eval()

# 웹캠에서 프레임 읽기 # todo : 오류 확인 할 것
cap = cv2.VideoCapture(0)
half_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
half_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
print(half_width, half_height)

largest_box_area = 0
largest_box_center = (0, 0)

smallest_box_area = float('inf')
smallest_box_center = (0, 0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    largest_box_area = 0  # 감지된 가장 큰 바운딩 박스의 면적
    largest_box_center = (0, 0)  # 가장 큰 바운딩 박스의 중심 좌표

    smallest_box_area = float('inf')  # 가장 작은 바운딩 박스의 면적
    smallest_box_center = (0, 0)  # 가장 작은 바운딩 박스의 중심 좌표

    closest_box_distance = float('inf')  # 가장 가까운 객체까지의 거리
    closest_box_center = (0, 0)  # 가장 가까운 객체의 중심 좌표

    for result in results.pred:
        for box in result[:, :4]:
            x_center = int((box[0] + box[2]) / 2)
            y_center = int((box[1] + box[3]) / 2)
            box_width = int(box[2] - box[0])
            box_heigt = int(box[3] - box[1])
            box_area = box_width * box_heigt

            # 가장 큰 바운딩 박스 갱신
            if box_area > largest_box_area:
                largest_box_area = box_area
                largest_box_center = (x_center, y_center)

            # 가장 작은 바운딩 박스 갱신
            if box_area < smallest_box_area:
                smallest_box_area = box_area
                smallest_box_center = (x_center, y_center)

            # 중심 좌표 갱신
            distance = math.sqrt((x_center - half_width)**2 + (y_center - half_height)**2)
            if distance < closest_box_distance:
                closest_box_distance = distance
                closest_box_center = (x_center, y_center)

            cv2.circle(frame, (x_center, y_center), 5, (0, 255, 0), -1)
            diag = math.sqrt((x_center - half_width)**2 + (y_center - half_height)**2)
            cv2.putText(frame, f'({int(((x_center - half_width)/diag)*100)}, {int(((y_center - half_height)/diag)*100)}, {int(diag)}, {box_area})', (x_center, y_center), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_8, False)

    # 가장 큰 바운딩 박스와 가장 작은 바운딩 박스의 면적 비교
    if largest_box_area < 1.2 * smallest_box_area:
        closest_box_center_str = f'Closest Box Center: {closest_box_center}'
        print(closest_box_center_str)
    else:
        largest_box_center_str = f'Largest Box Center: {largest_box_center}'
        print(largest_box_center_str)

    # 화면에 프레임 표시
    cv2.imshow("YOLOv5 Object Detection", frame)

    # 종료 키 확인
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 종료
cap.release()
cv2.destroyAllWindows()

if __name__ == '__main__':
    async def tester():
        async for single_coordinate in tree_finder.find_tree_coordinate():
            print(single_coordinate)
    
    tree_finder = FindTree()
    asyncio.run()