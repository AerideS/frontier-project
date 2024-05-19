import asyncio
import random
#import Jetson.GPIO as GPIO
import asyncio
import cv2
import numpy as np
import socket
import datetime

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
        

class LidarModule:
    '''
    라이다를 통해 거리 측정
    '''
    def __init__(self) -> None:
        pass
    
    async def getAltidude(self):
        print("MEASURING HEIGHT...")
        await asyncio.sleep(3)
        print("MEASURED  HEIGHT...")
        return 1999
    
    
    
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
    def __init__(self, save_directory='/home/jetson/Pictures/PiCamera_images'):
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
 
    # def __init__(self) -> None:
    #     self.status = False
    #     self.video_addr = "udp://127.0.0.1:5600"
    #     gst_str = ('nvarguscamerasrc sensor_id=0 wbmode=3 ! ' + 
    #        'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 ! ' + 
    #        'nvvidconv flip-method=0 ! ' + 
    #        'video/x-raw, width=960, height=540, ' + 
    #        'format=(string)BGRx ! ' +
    #        'videoconvert ! video/x-raw, format=BGR ! ' +
    #        'appsink').format(width, height)

    #     camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
    #     self.cap = cv2.VideoCapture(self.video_addr)
    #     # except 
        
    # def getPicture(self):
    #     ret, frame = self.cap.read()  
    #     if not ret:
    #         print(1)
    #         return
    #     cv2.imshow('', frame)      


    # # def __init__(self) -> None:
    # #     # 송신측의 IP 주소와 포트
    # #     self.send_host = '127.0.0.1'

    # #     # 수신측의 포트
    # #     self.recv_port = 5600
        
    # # def getPicture(self):

    # #     # 소켓 생성
    # #     recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # #     recv_socket.bind((self.send_host, self.recv_port))  # 수신할 IP와 포트 지정

    # #     while True:
    # #         # 이미지 수신
    # #         data, addr = recv_socket.recvfrom(65507)  # UDP 패킷 수신 (패킷 최대 크기)
    # #         if len(data) > 0:
    # #             # 바이트 데이터를 numpy 배열로 변환
    # #             img_array = np.frombuffer(data, dtype=np.uint8)
                
    # #             # 이미지 형태로 변환
    # #             img = cv2.imdecode(img_array, flags=cv2.IMREAD_COLOR)
                
    # #             # 이미지가 유효한 경우 표시
    # #             if img is not None:
    # #                 cv2.imshow('Received Image', img)
    # #                 if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
    # #                     break

    # #     cv2.destroyAllWindows()

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
