import os
import cv2
from datetime import datetime

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

class RaspiCAM:
    def __init__(self, save_directory='/home/jetson/Pictures/PiCamera_images'):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)
        self.camera = self.init_CAM()

    def init_CAM(self):
        width = CAM_WIDTH
        height = CAM_HEIGHT
        gst_str = ('nvarguscamerasrc sensor_id=0 wbmode=0 ! ' + 
           'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 ! ' + 
           'nvvidconv flip-method=0 ! ' + 
           'video/x-raw, width=960, height=540, ' + 
           'format=(string)BGRx ! ' +
           'videoconvert ! video/x-raw, format=BGR ! ' +
           'appsink').format(width, height)

        camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        if not camera.isOpened():
            print("카메라를 열 수 없습니다.")
            exit()
        return camera

    def getPicture(self):
        ret, frame = self.camera.read()
        if not ret:
            print("비디오 스트림을 읽을 수 없습니다.")
            return
        print('이미지 가져옴.')
        return frame
    
    def savePicture(self):
        frame = self.getPicture()
        # 현재 시간을 기반으로 파일 이름 생성
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"captured_image_{current_time}.jpg"
        image_path = os.path.join(self.save_directory, self.filename)
        cv2.imwrite(image_path, frame)
        print("이미지가 저장되었습니다:", image_path)
        return frame

    #이건 걍 넣었음
    def displayCAM(self):
        while True:
            ret, frame = self.camera.read()
            if not ret:
                print("비디오 스트림을 읽을 수 없습니다.")
                break

            cv2.imshow('Camera', frame)

            key = cv2.waitKey(1)
            if key == 27:
                break
            elif key == ord('s'):
                self.save_image()

        self.camera.release()
        cv2.destroyAllWindows()

# 사용 예시
if __name__ == "__main__":
    cam_module = RaspiCAM()
    # cam_module.getPicture()
    cam_module.savePicture()
    # cam_module.displayCAM()
