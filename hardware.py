import asyncio
import random
#import Jetson.GPIO as GPIO
import asyncio

class Dropper__STUB:
    def __init__(self) -> None:
        pass
    
    async def drop(self):
        await asyncio.sleep(5)
        print("DROP COMPLETE")
        

class LidarModule:
    '''
    라이다를 통해 거리 측정
    '''
    def __init__(self) -> None:
        pass
    
    def getAltidude(self):
        pass
    
    
    
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
        
        
        
class RaspiCAM__STUB:
    '''
    현재 웹캠에서 이미지 받아옴
    '''
    
    def __init__(self) -> None:
        pass
        
    async def getPicture(self):
        await asyncio.sleep(1)
        
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
        return (1, 1)
    