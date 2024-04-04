import pika, json

#서버 연결
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#exchange 선언
channel.exchange_declare(exchange='test_exchange', exchange_type='topic')

#메시지 전송 함수
def send_message(message_type, data=None):
    #라우팅키 설정
    routing_key = f"frontier.{message_type}"
    
    message = json.dumps(data)

    #메시지 송신
    channel.basic_publish(exchange='test_exchange', routing_key=routing_key, body=message)
    print(f"Sent message: {message}")

#테스트
send_message("ready", "this is ready")
send_message("takeoff", "this is takeoff")
send_message("land", "this is landing")
send_message("move", [{"lat": "37.7749", "lon": "-122.4194"}, {"lat": "38.8895", "lon": "-77.0352"}])
send_message("altitude", {"alt": "1000"})
send_message("drop", {"height": "500"})
send_message("mistake", "this is mistake")
# 연결 종료
connection.close()

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