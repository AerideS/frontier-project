import pika, json
import threading
import aio_pika
import asyncio

SERVER_IP = 'localhost'


'''
    # todo : 전송하다가 뻑나는 경우 있음, 서버 연결 실패 등등
    해당 경우 예외 처리 할 수 있을 것
'''


class MqReceiverAsync:
    def __init__(self, device_name, server_ip) -> None:
        self.server_ip = server_ip
        self.device_name = device_name

    async def getMessage(self):
        # RabbitMQ 연결 설정
        connection = await aio_pika.connect_robust(f"amqp://guest:guest@{self.server_ip}/")
        async with connection:
            # 채널 열기
            channel = await connection.channel()
            
            # 큐 선언
            queue = await channel.declare_queue(name=self.device_name, durable=True)
            
            # 메시지 받기
            async for message in queue:
                async with message.process():
                    # 메시지 처리
                    yield json.loads(message.body.decode())


class MqReceiver:
    '''
        #[요구사항]
        #1. mavSDK_api 코드에서 필요한 파라미터들을 알아야 한다.
        #2. 해당 데이터(파라미터들)을 포함하는 메시지를 producer에게 받아야 한다. (producer는 서버로부터 데이터를 받음)
        #3. 메시지에 포함된 파라미터를 이용하여 mavSDK_api 내부 함수를 호출해야 한다.

        #[이 코드의 작동방식 및 역할]
        #1. producer로부터 mavSDK_api를 운영하기 위한 파라미터가 포함된 메시지를 받는다.
        #2. 라우팅 키(test.takeoff, test.land 등)를 기준으로 미션을 구분하여 함수(takeoff, land 등)가 작동한다.
            # *** 미션: 드론의 모든 동작(준비, 이륙, 이동, 착륙 등) ***
            # *** 한 메시지당 하나의 미션에 대한 데이터를 가지고 있다. ***
        #3. 함수(takeoff, land 등)에는 mavSDK_api에 존재하는 함수를 이용하여 드론을 동작시킨다. 
        #4. 한 미션이 끝날 때마다 producer에게 메시지 처리 완료를 통지한다.

        # *** 정리하면 이 코드는 producer에세 메시지를 받아 mavSDK_api를 이용하여 직접적으로 드론에게 동작을 명령하는 역할을 한다. ***
    
    '''
    
    def __init__(self, exchange, server_ip) -> None:
        self.exchange_name = exchange
        self.server_ip = server_ip
        self.connect_Server()
        self.createQueue()
        #self.start()
    
    def connect_Server(self):

        # 서버 연결
        # todo 본 부분에 서버 연결 실패시 예외처리 필요
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.server_ip))
        self.channel = self.connection.channel()

        #exchange 선언
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

    def createQueue(self):

        #큐 생성
        result=self.channel.queue_declare(queue=self.exchange_name, durable=True) 
        #durable=True : 큐가 영속적인 것의 의미, 해당 큐를 디스크에 저장하고, 서버가 재시작되어도 큐와 큐에 포함된 메시지가 유지
        
        # #임시 큐 생성
        # result = channel.queue_declare('', exclusive=True)
        # 헤당 큐 이름 저장
        queue_name = result.method.queue

        #바인딩 키 설정(확장성을 고려하여 리스트로 함)
        binding_keys = ["frontier.*"]

        #바인딩
        for binding_key in binding_keys:
            self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=binding_key)

        
    def callback(self, ch, method, properties, body):
        #byte -> dictionary 변환
        decoded_body = body.decode('utf-8')
        dictionary_body = json.loads(decoded_body)

        #라우팅 키 
        routing_key = method.routing_key

        #goto
        if routing_key == "frontier.goto":
            print(" [x] Received 'goto' message:", dictionary_body)
        
        #setElev
        elif routing_key == "frontier.setElev":
            print(" [x] Received 'setElev' message:", dictionary_body)

        #wait
        elif routing_key == "frontier.wait":
            print(" [x] Received 'wait' message:", dictionary_body)

        #takeoff
        elif routing_key == "frontier.takeoff":
            print(" [x] Received 'takeoff' message:", dictionary_body)

        #land
        elif routing_key == "frontier.land":
            print(" [x] Received 'land' message:", dictionary_body)

        #arm
        elif routing_key == "frontier.arm":
            print(" [x] Received 'arm' message:", dictionary_body)

        #disarm
        elif routing_key == "frontier.disarm":
            print(" [x] Received 'disarm' message:", dictionary_body)

        #startDrop
        elif routing_key == "frontier.startDrop":
            print(" [x] Received 'startDrop' message.", dictionary_body)

        else:
            print(f" [x] Received unknown message: {routing_key}: {dictionary_body}")
        
    def start(self):
        # 메시지 수신
        self.channel.basic_consume(queue=self.exchange_name, on_message_callback=self.callback, auto_ack=True)

        # 메시지 처리 시작
        self.channel.start_consuming()
        
    async def getMessage(self):
        '''
        메세지가 들어올때까지 대기하다 메세지를 받을 경우 메세지 반환
        '''        
        method_frame, header_frame, body = None, None, None
        print("waiting for message")
        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.exchange_name, auto_ack=True)
            if method_frame:
                break
            
            yield body.decode() 

class MqSender:
    '''
        #[요구사항]
        #1. 서버에서 보낸 데이터를 받아야 한다.
        #2. 데이터에 포함된 미션넘버를 기준으로 라우팅 키를 설정하여야 한다. 즉, 미션에 따라 라우팅 키가 다름(ex) test.미션이름)
        #3. 미션 순서대로 consumer에게 메시지를 보내야 한다.

        #[이 코드의 작동방식 및 역할]
        #1. 서버로부터 데이터를 받는다
        #2. json 형식의 데이터에서 

        #[서버에서 보내는 데이터 포멧]


        #명령에 따라 받아야 하는 데이터
        #1. 이륙 : set_takeoff_altitude(altitude), takeoff())
        #2. 착륙 : Action.return_to_launch(), async set_return_to_launch_altitude(relative_altitude_m), Action.land()
        #3. 이동 : goto_location(latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
        #         -> absolute_altitude_m(평균 해수면 기준), yaw_deg(NED좌표계, 북쪽이 0도, 시계방향이 양)
        #4. 고도 조정 : 
        #5. 투하 : 
        
        # todo, 대상 이름 지정할 수 있도록 할 것
    '''
    def __init__(self, exchange, server_ip) -> None:
        self.exchange_name = exchange
        self.server_ip = server_ip
        self.connect_Server()
    
    def connect_Server(self):

        #서버 연결
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.server_ip))
        self.channel = self.connection.channel()

        #exchange 선언
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')
        
    #메시지 전송 함수
    def send_message(self, message_type, data=None):
        #라우팅키 설정
        routing_key = f"frontier.{message_type}"
        
        message = json.dumps(data)

        #메시지 송신
        self.channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key, body=message)
        print(f" Sent message: {message}")
        
    def arm(self):
        # todo ... 명령별로 함수 구성 및 파라미터 받도록 해야 함
        message = {
            'type' : 'arm'
            }
        self.send_message("arm", message)
    
    def takeoff(self, altitude):
        message = {
            'type' : 'takeoff',
            'altitude' : altitude
        }
        self.send_message("takeoff", message)
    
    def goto(self, latitude, longitude):
        message = {
            'type' : 'goto',
            'latitude' : latitude,
            'longitude' : longitude
        }
        self.send_message("goto", message)
        
    def setElev(self, altitude):
        message = {
            'type' : 'setElev',
            'altitude' : altitude
        }
        self.send_message("setElev", message)

    def wait(self, time):
        message = {
            'type' : 'wait',
            'time' : time
        }
        self.send_message("wait", message)

    def land(self):
        message = {
            'type' : 'land'
            }
        self.send_message("land", message)

    def disarm(self):
        message = {
            'type' :'disarm'
            }
        self.send_message("disarm", message)
    
    def startDrop(self, latitude, longitude):
        message = {
            'type' : 'startDrop',
            'latitude' : latitude,
            'longitude' : longitude
        }
        self.send_message("startDrop", message)


    def close(self):
        self.connection.close()


import time

#테스트용 함수!
def test_receiver():
    receiver = MqReceiver('drone1', 'localhost')
    receiver.start()

def test_sender():
    sender = MqSender('drone1', 'localhost')

    time.sleep(1)
    sender.arm()
    time.sleep(1)
    sender.takeoff(30)
    # time.sleep(1)
    # sender.goto(35.1541529, 128.0929031)
    # time.sleep(1)
    # sender.setElev(50)
    # time.sleep(1)
    # sender.wait(60)
    # time.sleep(1)
    # sender.land()
    # time.sleep(1)
    # sender.disarm()
    # time.sleep(1)
    # sender.startDrop(35.1541529, 128.0929031)
    # time.sleep(1)
    # sender.send_message('mistake', 'I am mistake')

    # 연결 종료
    sender.connection.close()

if __name__ == '__main__':
    # 테스트 수행
    TEST = 1
    if TEST == 1:
        # test_sender_receiver 함수를 쓰레드로 실행
        # threading.Thread(target=test_receiver).start()
        threading.Thread(target=test_sender).start()
    else:
        receiver = MqReceiver('test_queue', 'localhost')
        receiver.start()