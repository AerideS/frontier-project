import pika
import time

#서버 연결
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

#exchange 선언
channel.exchange_declare(exchange='test_exchange', exchange_type='topic')

#임시 큐 생성
result = channel.queue_declare('', exclusive=True)
# 헤당 큐 이름 저장
queue_name = result.method.queue

#라우팅 키 설정(확장성을 고려하여 리스트로 함)
binding_keys = ["test.#"]

#바인딩
for binding_key in binding_keys:
    channel.queue_bind(exchange='test_exchange', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')

# 메시지 처리 함수
def callback(ch, method, properties, body):
    routing_key = method.routing_key
    #takeoff
    if routing_key == "test.takeoff":
        print(" [x] Received 'takeoff' message:", body)
        print(type(body))
    #land
    elif routing_key == "test.land":
        print(" [x] Received 'land' message:", body)
        print(type(body))
    #move
    elif routing_key == "test.move":
        print(" [x] Received 'move' message:", body)
        print(type(body))
    #altitude
    elif routing_key == "test.altitude":
        print(" [x] Received 'altitude' message:", body)
        print(type(body))
    #drop
    elif routing_key == "test.drop":
        print(" [x] Received 'drop' message. Dropping the message:", body)
        print(type(body))
    else:
        print(f" [x] Received unknown message: {routing_key}: {body}")
        print(type(body))

# 메시지 수신
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# 메시지 처리 시작
channel.start_consuming()

#상현이가 짠 mavSDK 코드에서 필요한 파라미터들을 알아야 한다.
#해당 파라미터들은 최초에 사용자(서버)로부터 얻고 consumer.py에서는 해당 파라미터들을 producer.py로부터 받아 저장해두어야 한다.
#저장된 파라미터들이 mavSDK 코드에서 사용되어 드론이 임무를 수행하게 될 것이다.

#필요한 드론 동작에는 무엇이 있지??
#1. 이륙 
#2. 착륙 
#3. 이동 : waypoint를 1개 이상 지정해야 할 거임(따라서 위도/경도 리스트가 필요하다)
#4. 고도 조정 -> 상승 또는 하강할 높이값
#5. 투하 : mavSDK와 관련은 없지만 해당 명령을 받으면 모터/열선 작동해야함 -> 나무로부터의 높이, 모터 회전 속도(상수), 높이와 회전 속도로 구한 회전시간