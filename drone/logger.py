import logging
import sys
from datetime import datetime

class DroneLogger:
    '''
    DEBUG: 프로그램 작동에 대한 상세한 정보를 가지는 로그. 문제의 원인을 파악할 때에만 이용.
    INFO: 프로그램 작동이 예상대로 진행되고 있는지 트래킹하기 위해 사용.
    WARNING: 예상치 못한 일이나 추후 발생 가능한 문제를 표시하기 위함.
    ERROR: 심각한 문제로 인해 프로그램이 의도한 기능을 수행하지 못하고 있는 상황을 표시.
    CRITICAL: 더욱 심각한 문제로 인해 프로그램 실행 자체가 언제라도 중단될 수 있음을 표시.
    '''
    def __init__(self) -> None:
        self.logger = logging.basicConfig(filemode=f'./logs/log_{str(datetime.now().timestamp())}', 
                                          format='%(asctime)s %(levelname)s %(message)s %(lineno)d %(pathname)s %(processName)s %(threadName)s',
                                          level=logging.DEBUG, 
                                          datefmt='%m/%d/%Y %I:%M:%S %p',)


