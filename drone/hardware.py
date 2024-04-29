import asyncio
import random
#import Jetson.GPIO as GPIO
import asyncio
import cv2

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
        await asyncio.sleep(1)
        
        return_alt = random.randint(3, 8)
        return return_alt
        
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
        
class RaspiCAM__STUB:
    '''
    현재 웹캠에서 이미지 받아옴
    '''
    
    def __init__(self) -> None:
        pass
        
    def getPicture(self):
        
        
        picture = None
        return picture
        
    
class FindTree__STUB:
    '''
    
    '''
    def __init__(self) -> None:
        '''
        초기화 과정, 
        '''
        pass
    
    async def find_tree_coordinate(self, image):
        '''
        작동 과정
        카메라 읽기 -> 이미지 객체 판독 -> 박스 결과 yield로 반환하기 반복
        '''
        print('find_tree_coordinate')
        return 1, 1
    
    
if __name__ == '__main__':
    cam = RaspiCAM()
    cam.getPicture()
