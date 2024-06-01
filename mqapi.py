import pika, json, time
import threading
import aio_pika
import asyncio
from mongodb_api import DroneData
import logging

# SERVER_IP = 'localhost'
'''
서버 주소 
'''

CONNECTION_CHECK_PERIOD = 3
'''
서버와의 연결 확인 주기
'''

RETRY_PERIOD = 3
'''
서버 접속 시도 실패시 재시도까지의 시간
'''

'''
    # todo : 전송하다가 뻑나는 경우 있음, 서버 연결 실패 등등
    해당 경우 예외 처리 할 수 있을 것
'''


class MqReceiverAsync:
    def __init__(self, device_name, server_ip) -> None:
        self.server_ip = server_ip
        self.device_name = device_name
        self._keep_going = True
        self.connected = False
        self.connection = None
        
    async def initConnection(self):
        '''
        연결을 초기화하는 함수 
        서버와 연결되지 않은 경우 발생할 수 있는 예외에 대한 처리 필요        
        '''
        while True:
            try:
                self.connection = await aio_pika.connect_robust(f"amqp://drone:1234@{self.server_ip}/")
                self.channel = await self.connection.channel()
                await self.channel.queue_delete(queue_name=self.device_name)
                self.queue = await self.channel.declare_queue(name=self.device_name, durable=True)
                
                self.connected = True
                break
            except aio_pika.exceptions.AMQPConnectionError as err:
                print(err, "error while checking connection to server")
                await asyncio.sleep(RETRY_PERIOD)
            finally:
                logging.debug("rabbitmq init complete")
                await self.connection.close()
        
    async def checkConnection(self):
        try:
            while True:
                try:
                    self.connection = await aio_pika.connect_robust(f"amqp://drone:1234@{self.server_ip}/")
                    self.channel = await self.connection.channel()
                    self.queue = await self.channel.declare_queue(name=self.device_name, durable=True)
                    
                    yield True # 연결이 확인되었을 때, 정상연결 될 때
                except aio_pika.exceptions.AMQPConnectionError as err:
                    print(err, "error while checking connection to server")
                    yield False
                
                await asyncio.sleep(CONNECTION_CHECK_PERIOD)
        except asyncio.CancelledError as err:
            print(err, "connection check canceled")
            
        
    async def getMessage(self):
        # RabbitMQ 연결 설정
        
        try:
            self.connection = await aio_pika.connect_robust(f"amqp://drone:1234@{self.server_ip}/")
            self.connected = True
            print('connected', self.connected, self.server_ip)
            async with self.connection:
                # 채널 열기
                self.channel = await self.connection.channel()
                print(31)
                # 큐 선언
                self.queue = await self.channel.declare_queue(name=self.device_name, durable=True)
                print(34)
                # 메시지 받기
                async for message in self.queue:
                    # if self._keep_going is False:
                    #     break
                    async with message.process():
                        # 메시지 처리
                        logging.debug(f"Message got : {message.body.decode()}")
                        yield json.loads(message.body.decode())
        except Exception as excpt:
            print(excpt)
                        
        finally:
            if self.connected:
                await self.connection.close()
                self.connected = False
            
            
    async def stop(self):
        self._keep_going = False
        
class MqSenderAsync:
    def __init__(self, server_ip) -> None:
        self.server_ip = server_ip
        self._keep_going = True
        print('------------',self.server_ip, self._keep_going)
        
    async def send_message(self, message, target):
        # RabbitMQ 서버에 연결
        connection = await aio_pika.connect_robust(
            f"amqp://drone:1234@{self.server_ip}/",  # RabbitMQ 서버 주소 및 계정 정보
            loop=asyncio.get_event_loop()
        )

        try:
            # 연결된 채널 생성
            async with connection:
                # 채널에서 메시지를 보낼 큐 생성
                channel = await connection.channel()

                queue = await channel.declare_queue(name=target, durable=True)

                logging.debug(f'message : {str(message)}, to {target}')

                message_body = json.dumps(message)

                await channel.default_exchange.publish(
                    aio_pika.Message(body=message_body.encode()),  
                    routing_key=queue.name 
                )
                print("Message sent:", 'to', target)

        finally:
            # 연결 종료
            await connection.close()
    
    # async def close(self):
    #     await self.connection.close()

class MqReceiver:
    def __init__(self, device_name, server_ip) -> None:
        self.server_ip = server_ip
        self.queue_name = device_name
        self._keep_going = True
        self.connected = False
        self.connection = None
        self.message = None

    def initConnection(self):
        '''
        서버 연결 초기화
        '''
        while True:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))
                self.channel = self.connection.channel()
                self.channel.queue_delete(queue=self.queue_name)
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                self.connected = True
                print(f"Connected to RabbitMQ server at {self.server_ip}, queue '{self.queue_name}' initialized.")
                break
            except pika.exceptions.AMQPConnectionError as err:
                print(err, "error while trying to connect to server")
                time.sleep(RETRY_PERIOD)
            except Exception as err:
                print(err, "an unexpected error occurred during connection initialization")
            finally:
                if self.connection and not self.connection.is_closed:
                    self.connection.close()

    def check_connection(self):
            try:
                while True:
                    try:
                        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))
                        self.channel = self.connection.channel()
                        self.channel.queue_declare(queue=self.queue_name, durable=True)
                        
                        yield True # 연결이 확인되었을 때, 정상 연결될 때
                    except pika.exceptions.AMQPConnectionError as err:
                        print(err, "error while checking connection to server")
                        yield False
                    
                    time.sleep(CONNECTION_CHECK_PERIOD)
            except Exception as err:
                print(err, "connection check canceled")

    def get_message(self):
        '''
        메시지를 수신하고 처리하는 함수
        '''
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))
            self.channel = self.connection.channel()
            result = self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            def callback(ch, method, properties, body):
                '''
                메시지 처리
                '''
                message = json.loads(body.decode())
                if message['type'] == 'status':
                    device_data = DroneData()
                    # time = message['time']
                    device_id = message['device']
                    latitude = message['position']['latitude_deg']
                    longitude = message['position']['longitude_deg']
                    altitude = message['position']['absolute_altitude_m']
                    # rel_altitude = message['position']['relative_altitude_m']
                    # vel_north = message['velocity']['north_m_s']
                    # vel_east = message['velocity']['east_m_s']
                    # vel_down = message['velocity']['down_m_s']
                    # voltage = message['battery']['voltage_v']
                    # current = message['battery']['current_battery_a']
                    # remain = message['battery']['remaining_percent']

                    # 데이터베이스 업데이트
                    device_data.update_device_data(device_id, longitude, latitude, altitude)
        
                print("Received message:", message, "from ", self.queue_name, 'queue')

            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            
            print('Waiting for messages...')
            self.channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as err:
            print(err, "error while receiving messages from server")
        except Exception as excpt:
            print(excpt)
        finally:
            if self.connected:
                self.connection.close()
                self.connected = False

def stop(self):
    self._keep_going = False
    if self.channel:
        self.channel.stop_consuming()
    if self.connection and self.connection.is_open:
        self.connection.close()

class MqSender:
    def __init__(self, server_ip) -> None:
        self.server_ip = server_ip
        self._keep_going = True
        print('------------', self.server_ip, self._keep_going)
    
    def send_message(self, message, target):
        # RabbitMQ 서버에 연결
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server_ip))

        try:
            # 연결된 채널 생성
            channel = connection.channel()

            # 채널에서 메시지를 보낼 큐 생성
            channel.queue_declare(queue=target, durable=True)

            message_body = json.dumps(message)

            channel.basic_publish(
                exchange='',
                routing_key=target,
                body=message_body.encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 메시지 영구 저장
                ))
            print("Message sent ", 'to', target, ": ", message)

        finally:
            # 연결 종료
            connection.close()
    def arm(self, target):
        # todo ... 명령별로 함수 구성 및 파라미터 받도록 해야 함
        message = {
            'type' : 'arm'
            }
        self.send_message(message, target)
    
    def takeoff(self, altitude, target):
        message = {
            'type' : 'takeoff',
            'altitude' : altitude
        }
        self.send_message(message, target)
    
    def goto(self, latitude, longitude, target):
        message = {
            'type' : 'goto',
            'latitude' : latitude,
            'longitude' : longitude
        }
        self.send_message(message, target)
        
    def setElev(self, altitude, target):
        message = {
            'type' : 'setElev',
            'altitude' : altitude
        }
        self.send_message(message, target)

    def wait(self, time, target):
        message = {
            'type' : 'wait',
            'time' : time
        }
        self.send_message(message, target)

    def land(self, target):
        message = {
            'type' : 'land'
            }
        self.send_message(message, target)

    def disarm(self, target):
        message = {
            'type' :'disarm'
            }
        self.send_message(message, target)
    
    def startDrop(self, latitude, longitude, target):
        message = {
            'type' : 'startDrop',
            'latitude' : latitude,
            'longitude' : longitude
        }
        self.send_message(message, target)

    def cutString(self, target):
        message = {
            'type' : 'cutString'
            }
        self.send_message(message, target)

    def ascent_repeater(self, target):
        message = {
            'type' : 'ascent_repeater'
        }
        self.send_message(message, target)

    def descent_repeater(self, target):
        message = {
            'type' : 'descent_repeater'
        }
        self.send_message(message, target)

# class MqReceiver:
#     '''
#         #[요구사항]
#         #1. mavSDK_api 코드에서 필요한 파라미터들을 알아야 한다.
#         #2. 해당 데이터(파라미터들)을 포함하는 메시지를 producer에게 받아야 한다. (producer는 서버로부터 데이터를 받음)
#         #3. 메시지에 포함된 파라미터를 이용하여 mavSDK_api 내부 함수를 호출해야 한다.

#         #[이 코드의 작동방식 및 역할]
#         #1. producer로부터 mavSDK_api를 운영하기 위한 파라미터가 포함된 메시지를 받는다.
#         #2. 라우팅 키(test.takeoff, test.land 등)를 기준으로 미션을 구분하여 함수(takeoff, land 등)가 작동한다.
#             # *** 미션: 드론의 모든 동작(준비, 이륙, 이동, 착륙 등) ***
#             # *** 한 메시지당 하나의 미션에 대한 데이터를 가지고 있다. ***
#         #3. 함수(takeoff, land 등)에는 mavSDK_api에 존재하는 함수를 이용하여 드론을 동작시킨다. 
#         #4. 한 미션이 끝날 때마다 producer에게 메시지 처리 완료를 통지한다.

#         # *** 정리하면 이 코드는 producer에세 메시지를 받아 mavSDK_api를 이용하여 직접적으로 드론에게 동작을 명령하는 역할을 한다. ***
    
#     '''
    
#     def __init__(self, queue_name, server_ip) -> None:
#         self.queue_name = queue_name
#         self.server_ip = server_ip
#         self.connect_Server()
#         self.createQueue()
#         #self.start()
    
#     def connect_Server(self):

#         # 서버 연결
#         # todo 본 부분에 서버 연결 실패시 예외처리 필요
#         self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.server_ip))
#         self.channel = self.connection.channel()

#     def createQueue(self):

#         #큐 생성
#         result=self.channel.queue_declare(queue=self.queue_name, durable=True) 
#         #durable=True : 큐가 영속적인 것의 의미, 해당 큐를 디스크에 저장하고, 서버가 재시작되어도 큐와 큐에 포함된 메시지가 유지
        
#         # #임시 큐 생성
#         # result = channel.queue_declare('', exclusive=True)
#         # 헤당 큐 이름 저장
#         queue_name = result.method.queue

#         #바인딩 키 설정(확장성을 고려하여 리스트로 함)
#         binding_keys = ["frontier.*"]

#         #바인딩
#         for binding_key in binding_keys:
#             self.channel.queue_bind(exchange=self.queue_name, queue=queue_name, routing_key=binding_key)

        
#     def callback(self, ch, method, properties, body):
#         print('callback')
#         #byte -> dictionary 변환
#         decoded_body = body.decode('utf-8')
#         dictionary_body = json.loads(decoded_body)
#         print(dictionary_body)
#         #라우팅 키 
#         routing_key = method.routing_key

#         #goto
#         if routing_key == "frontier.goto":
#             print(" [x] Received 'goto' message:", dictionary_body)
        
#         #setElev
#         elif routing_key == "frontier.setElev":
#             print(" [x] Received 'setElev' message:", dictionary_body)

#         #wait
#         elif routing_key == "frontier.wait":
#             print(" [x] Received 'wait' message:", dictionary_body)

#         #takeoff
#         elif routing_key == "frontier.takeoff":
#             print(" [x] Received 'takeoff' message:", dictionary_body)

#         #land
#         elif routing_key == "frontier.land":
#             print(" [x] Received 'land' message:", dictionary_body)

#         #arm
#         elif routing_key == "frontier.arm":
#             print(" [x] Received 'arm' message:", dictionary_body)

#         #disarm
#         elif routing_key == "frontier.disarm":
#             print(" [x] Received 'disarm' message:", dictionary_body)

#         #startDrop
#         elif routing_key == "frontier.startDrop":
#             print(" [x] Received 'startDrop' message.", dictionary_body)

#         else:
#             print(f" [x] Received unknown message: {routing_key}: {dictionary_body}")
        

#     def start(self):
#         # 메시지 수신
#         self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
#         print(187)
#         # 메시지 처리 시작
#         self.channel.start_consuming()
        
#     async def getMessage(self):
#         '''
#         메세지가 들어올때까지 대기하다 메세지를 받을 경우 메세지 반환
#         '''        
#         method_frame, header_frame, body = None, None, None
#         print("waiting for message")
#         while True:
#             method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
#             if method_frame:
#                 break
            
#             yield body.decode() 

# class MqSender:
#     '''
#         #[요구사항]
#         #1. 서버에서 보낸 데이터를 받아야 한다.
#         #2. 데이터에 포함된 미션넘버를 기준으로 라우팅 키를 설정하여야 한다. 즉, 미션에 따라 라우팅 키가 다름(ex) test.미션이름)
#         #3. 미션 순서대로 consumer에게 메시지를 보내야 한다.

#         #[이 코드의 작동방식 및 역할]
#         #1. 서버로부터 데이터를 받는다
#         #2. json 형식의 데이터에서 

#         #[서버에서 보내는 데이터 포멧]


#         #명령에 따라 받아야 하는 데이터
#         #1. 이륙 : set_takeoff_altitude(altitude), takeoff())
#         #2. 착륙 : Action.return_to_launch(), async set_return_to_launch_altitude(relative_altitude_m), Action.land()
#         #3. 이동 : goto_location(latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
#         #         -> absolute_altitude_m(평균 해수면 기준), yaw_deg(NED좌표계, 북쪽이 0도, 시계방향이 양)
#         #4. 고도 조정 : 
#         #5. 투하 : 
        
#         # todo, 대상 이름 지정할 수 있도록 할 것
#     '''
#     def __init__(self, queue_name, server_ip) -> None:
#         self.queue_name = queue_name
#         self.server_ip = server_ip
#         self.connect_Server()
    
#     def connect_Server(self):

#         #서버 연결
#         self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.server_ip))
#         self.channel = self.connection.channel()

#         #exchange 선언
#         self.exchange =  self.channel.exchange_declare(exchange=self.queue_name, exchange_type='topic')
        
#         binding_keys = ["frontier.*"]

#         #바인딩
#         for binding_key in binding_keys:
#             self.channel.queue_bind(self.queue_name, self.queue_name, routing_key=binding_key)
        
#     #메시지 전송 함수
#     def send_message(self, message_type, data=None):
#         #라우팅키 설정
#         routing_key = f"frontier.{message_type}"
        
#         message = json.dumps(data)
        

#         #메시지 송신
#         self.channel.basic_publish(exchange=self.queue_name, routing_key=routing_key, body=message)
#         print(f" Sent message: {message} to {self.queue_name}")
        
#     def arm(self):
#         # todo ... 명령별로 함수 구성 및 파라미터 받도록 해야 함
#         message = {
#             'type' : 'arm'
#             }
#         self.send_message("arm", message)
    
#     def takeoff(self, altitude):
#         message = {
#             'type' : 'takeoff',
#             'altitude' : altitude
#         }
#         self.send_message("takeoff", message)
    
#     def goto(self, latitude, longitude):
#         message = {
#             'type' : 'goto',
#             'latitude' : latitude,
#             'longitude' : longitude
#         }
#         self.send_message("goto", message)
        
#     def setElev(self, altitude):
#         message = {
#             'type' : 'setElev',
#             'altitude' : altitude
#         }
#         self.send_message("setElev", message)

#     def wait(self, time):
#         message = {
#             'type' : 'wait',
#             'time' : time
#         }
#         self.send_message("wait", message)

#     def land(self):
#         message = {
#             'type' : 'land'
#             }
#         self.send_message("land", message)

#     def disarm(self):
#         message = {
#             'type' :'disarm'
#             }
#         self.send_message("disarm", message)
    
#     def startDrop(self, latitude, longitude):
#         message = {
#             'type' : 'startDrop',
#             'latitude' : latitude,
#             'longitude' : longitude
#         }
#         self.send_message("startDrop", message)

#     def cutString(self):
#         message = {
#             'type' : 'cutString'
#             }
#         self.send_message("cutString", message)

#     def startReel(self):
#         message = {
#             'type' : 'startReel'
#         }
#         self.send_message("startReel", message)
        
#     def close(self):
#         self.connection.close()

async def test_receiver_async():
    receiver = MqReceiverAsync('drone1', 'localhost')
    await receiver.initConnection()
    async for message in receiver.getMessage():
        print(message)
    
async def checkConnect():
    receiver = MqReceiverAsync('drone1', 'localhost')
    async for message in receiver.checkConnection():
        print(message)
    
#테스트용 함수!
def test_receiver():
    # asyncio.run(test_receiver_async())
    receiver = MqReceiver('drone1', 'localhost')
    receiver.start()

def test_sender():
    '''
    DEMO
    start point : 35.15970, 128.082627
    --- draw square
    first Point : 35.15975, 128.082627
    second point: 35.15975, 128.082622
    third Point : 35.15970, 128.082622
    fourth Point: 35.15970, 128.082627
    --- seek Tree : 35.15970, 128.082627   
    '''

    # sender = MqSender('drone1', 'localhost')
    sender = MqSender('localhost')
    # time.sleep(5)
    # sender.arm("SERVER")
    # sender.takeoff(7, "SERVER")
    # sender.goto(35.15970, 128.082627, "SERVER")
    
    # sender.startDrop(35.15960, 128.082627)
    
    # sender.goto(35.15970, 128.082540)
    # sender.goto(35.15970, 128.082550)
    # sender.goto(35.15970, 128.082560)
    # sender.goto(35.15970, 128.082570)
    # sender.goto(35.15970, 128.082580)
    # sender.goto(35.15970, 128.082590)
    # sender.goto(35.15970, 128.082600)
    
    # sender.goto(35.15970, 128.082610)
    # sender.goto(35.15970, 128.082620)
    # sender.goto(35.15970, 128.082630)
    # sender.goto(35.15970, 128.082640)
    # sender.goto(35.15970, 128.082650)
    
    # sender.goto(35.15970, 128.082540)
    # sender.goto(35.15970, 128.082550)
    # sender.goto(35.15970, 128.082560)
    # sender.goto(35.15970, 128.082570)
    # sender.goto(35.15970, 128.082580)
    # sender.goto(35.15970, 128.082590)
    # sender.goto(35.15970, 128.082600)
    
    # sender.goto(35.15970, 128.082610)
    # sender.goto(35.15970, 128.082620)
    # sender.goto(35.15970, 128.082630)
    # sender.goto(35.15970, 128.082640)
    # sender.goto(35.15970, 128.082650)
    
    # sender.goto(35.15970, 128.082540)
    # sender.goto(35.15970, 128.082550)
    # sender.goto(35.15970, 128.082560)
    # sender.goto(35.15970, 128.082570)
    # sender.goto(35.15970, 128.082580)
    # sender.goto(35.15970, 128.082590)
    # sender.goto(35.15970, 128.082600)
    
    # sender.goto(35.15970, 128.082610)
    # sender.goto(35.15970, 128.082620)
    # sender.goto(35.15970, 128.082630)
    # sender.goto(35.15970, 128.082640)
    # sender.goto(35.15970, 128.082650)
    

    # sender.wait(2)
    # sender.goto(35.15975, 128.082627)
    # sender.goto(35.15975, 128.082622)
    # sender.goto(35.15970, 128.082622)
    # sender.goto(35.15970, 128.082627)
    # sender.startDrop(35.15970, 128.082627, "SERVER")
    # sender.land("SERVER")

    data =  {
            "type" : "status",
            "time" : 'time',
            "device" : 'drone1',
            "position" : {
                "latitude_deg" : 35.115,
                "longitude_deg" : 128.555,
                "absolute_altitude_m" : 30,
                "relative_altitude_m" : 'rel_altitude'
            },
            "velocity" : {
                "north_m_s" : 'vel_north',
                "east_m_s" : 'vel_east',
                "down_m_s" : 'vel_down'
            },
            "battery" : {
                "voltage_v" : 'voltage',
                "current_battery_a" : 'current',
                "remaining_percent" : 'remain'
            }
        }
    sender.send_message(data, 'SERVER')

    # # time.sleep(10)
    # # asyncio.run(sender.send_message(1111, "SERVER"))
    # sender.startDrop(None, None)
    # # time.sleep(1)
    # sender.goto(35.1541529, 128.0929031)
    # # time.sleep(1)
    # sender.setElev(50)
    # # time.sleep(1)
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
    # sender.connection.close()

if __name__ == '__main__':
    # 테스트 수행
    TEST = 1
    if TEST == 1:
        # test_sender_receiver 함수를 쓰레드로 실행
        # threading.Thread(target=test_receiver).start()
        threading.Thread(target=test_sender).start()
        # test_sender()
        # asyncio.run(test_receiver_async())
    else:
        receiver = MqReceiver('drone1', 'localhost')
        receiver.start()