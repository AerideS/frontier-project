import pika, json

#서버 연결
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#exchange 선언
channel.exchange_declare(exchange='test_exchange', exchange_type='topic')

#메시지 전송 함수
def send_message(message_type, data=None):
    #라우팅키 설정
    routing_key = f"test.{message_type}"

    #메시지 정의
    message = json.dumps(data)

    #메시지 송신
    channel.basic_publish(exchange='test_exchange', routing_key=routing_key, body=message)
    print(f"Sent message: {message}")

#테스트
send_message("takeoff", "this is takeoff")
send_message("land", "this is landing")
send_message("move", [{"lat": "37.7749", "lon": "-122.4194"}, {"lat": "38.8895", "lon": "-77.0352"}])
send_message("altitude", {"alt": "1000"})
send_message("drop", {"height": "500"})
send_message("mistake", "this is mistake")
# 연결 종료
connection.close()


#경현이가 만든 서버에서 보낸 데이터를 받고 그 데이터를 바로 consumer.py로 보내야함
#명령에 따라 받아야 하는 데이터
#1. 이륙 : set_takeoff_altitude(altitude), takeoff())
#2. 착륙 : Action.return_to_launch(), async set_return_to_launch_altitude(relative_altitude_m), Action.land()
#3. 이동 : goto_location(latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
#         -> absolute_altitude_m(평균 해수면 기준), yaw_deg(NED좌표계, 북쪽이 0도, 시계방향이 양)
#4. 고도 조정 : 
#5. 투하 : 