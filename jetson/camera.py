import os
import cv2

# 저장할 디렉토리 경로 설정
save_directory = '/home/jetson/Pictures/PiCamera_images'

# 디렉토리가 존재하지 않으면 생성
os.makedirs(save_directory, exist_ok=True)

# 카메라 초기화
width = 1920
height = 1080

gst_str = ('nvarguscamerasrc sensor_id=0 ! ' + 
           'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 ! ' + 
           'nvvidconv flip-method=0 ! ' + 
           'video/x-raw, width={}, height={}, ' + 
           'format=(string)BGRx ! ' +
           'videoconvert ! video/x-raw, format=BGR ! ' +
           'appsink').format(width, height)

camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

if not camera.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 이미지 촬영 및 화면 표시
while True:
    ret, frame = camera.read()
    if not ret:
        print("비디오 스트림을 읽을 수 없습니다.")
        break

    cv2.imshow('Camera', frame)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('s'):
        image_path = os.path.join(save_directory, 'captured_image.jpg')
        cv2.imwrite(image_path, frame)
        print("이미지가 저장되었습니다:", image_path)

# 종료 시 카메라 해제 및 창 닫기
camera.release()
cv2.destroyAllWindows()
