import pika, json

#서버 연결
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

#exchange 선언
channel.exchange_declare(exchange='test_exchange', exchange_type='topic')

#큐 생성
result=channel.queue_declare(queue='test_queue', durable=True) #durable=True : 큐가 영속적인 것의 의미, 해당 큐를 디스크에 저장하고, 서버가 재시작되어도 큐와 큐에 포함된 메시지가 유지

# #임시 큐 생성
# result = channel.queue_declare('', exclusive=True)
# 헤당 큐 이름 저장
queue_name = result.method.queue

#바인딩 키 설정(확장성을 고려하여 리스트로 함)
binding_keys = ["frontier.#"]

#바인딩
for binding_key in binding_keys:
    channel.queue_bind(exchange='test_exchange', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')

#ready
def ready():
    print('이륙 전 아이들 상태까지 준비')
    #mavSDK_api 준비 관련 함수

#takeoff
def takeoff(altitude):
    print('이륙~~')
    #mavSDK_api 이륙 관련 함수

def land():
    print('착륙~~')
    #mavSDK_api 착륙 관련 함수

#move
def move(lat, lon, abs_alt):
    print('이동 가즈아~~')
    #mavSDK_api 이동 관련 함수

#adjust altitude
def adjust_alt(target_alt):
    print('고도 조정(이동을 동반함)')
    #mavSDK_api 현재 위치 받아오는 함수
    cur_lat = '현재 위도가 들어가야함'
    cur_lon = '현재 경도가 들어가야함'
    move(cur_lat, cur_lon, target_alt)

def drop():
    print('투하')
    #풀리 작동 및 열선 가열로 투하

# 메시지 처리 함수
def callback(ch, method, properties, body):
    #byte -> dictionary 변환
    decoded_body = body.decode('utf-8')
    dictionary_body = json.loads(decoded_body)

    #라우팅 키 
    routing_key = method.routing_key

    #move
    if routing_key == "test.move":
        print(" [x] Received 'move' message:", dictionary_body)

    #adjust altitude
    elif routing_key == "test.altitude":
        print(" [x] Received 'altitude' message:", dictionary_body)

    #takeoff
    elif routing_key == "test.takeoff":
        print(" [x] Received 'takeoff' message:", dictionary_body)

    #land
    elif routing_key == "test.land":
        print(" [x] Received 'land' message:", dictionary_body)

    #ready
    elif routing_key == "test.ready":
        print(" [x] Received 'ready' message:", dictionary_body)

    #drop
    elif routing_key == "test.drop":
        print(" [x] Received 'drop' message. Dropping the message:", dictionary_body)

    else:
        print(f" [x] Received unknown message: {routing_key}: {dictionary_body}")

# 메시지 수신
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# 메시지 처리 시작
channel.start_consuming()

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