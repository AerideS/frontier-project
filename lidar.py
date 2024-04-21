import asyncio
import random

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
        