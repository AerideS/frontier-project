import asyncio
import random
#import Jetson.GPIO as GPIO
import asyncio
import cv2
import numpy as np
import socket
import datetime
import os

class Dropper__STUB:
    def __init__(self) -> None:
        pass
    
    async def drop(self, height):
        print("DROPPER!", height)
        cnt = 0
        while cnt < 6:     
            print("dropping...")       
            await asyncio.sleep(1)
            cnt += 1
        
        print("DROP COMPLETE")
    
class LidarModule__STUB:
    '''
    라이다를 통해 거리 측정
    '''
    def __init__(self) -> None:
        pass
    
    async def getAltidude(self):
        print("MEASURING HEIGHT...")
        await asyncio.sleep(3)
        print("MEASURED  HEIGHT...")
        return 20
        
class RaspiCAM:
    '''
    현재 웹캠에서 이미지 받아옴
    '''
    
    def __init__(self) -> None:
        self.status = False
        # try:
        self.cap = cv2.VideoCapture(0)
        # except 
        
    def getPicture(self):
        ret, frame = self.cap.read()  
        if not ret:
            print(1)
            return
        cv2.imshow('', frame)      
        picture = None
        return picture  
        
class Cam_STUB_GAZEBO:
    def __init__(self, save_directory='./'):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)
        self.camera = self.init_CAM()

    def init_CAM(self):
        width = 1920
        height = 1080
        gst_str = ('nvarguscamerasrc sensor_id=0 wbmode=3 ! ' + 
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
        ret, frame = self.camera.read()
        if not ret:
            print("비디오 스트림을 읽을 수 없습니다.")
            return
        # 현재 시간을 기반으로 파일 이름 생성
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"captured_image_{current_time}.jpg"
        image_path = os.path.join(self.save_directory, self.filename)
        cv2.imwrite(image_path, frame)
        print("이미지가 저장되었습니다:", image_path)

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
 
class RaspiCAM__STUB:
    '''
    현재 웹캠에서 이미지 받아옴
    '''
    
    def __init__(self) -> None:
        pass
        
    def getPicture(self):
        '''
        예시 이미지 반환 
        '''
        picture = cv2.imread('./tree_example.png')
        return picture
        
if __name__ == '__main__':
    cam = Cam_STUB_GAZEBO()
    cam.getPicture()
