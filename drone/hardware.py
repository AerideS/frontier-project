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
    
    def __init__(self):
        self.gst_pipeline = (
        'udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 '
        '! rtph264depay ! avdec_h264 ! videoconvert ! appsink'
        )
        
    def getImage(self):
        return asyncio.run(self.getPicture())

    async def getPicture(self):

        cap = cv2.VideoCapture(self.gst_pipeline, cv2.CAP_GSTREAMER)

        # while not cap.isOpened():
        #     await asyncio.sleep(0.1)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
    
            # Display the frame
            # cv2.imshow('Frame', frame)

            # # Exit on 'q' key press
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # ret, frame = cap.read()
            # if not ret:
            #     print("Error: Could not read frame.")
            #     continue
            cv2.imshow("frame", frame)
            return frame
            
        cap.release()
        cv2.destroyAllWindows()
        return frame

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
    cv2.imwrite(f'./gz_image/image_{str(datetime.datetime.now().timestamp())}.png', cam.getImage(), [cv2.IMWRITE_JPEG_QUALITY, 90])
