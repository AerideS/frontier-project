
class networkChecker:
    '''
    주기적으로 서버에 ping을 보내어 서버와의 연결을 확인함
    마지막으로 ping을 보낸 시간을 저장.
    현재 시간이 마지막 ping 시간 + 주기 시간 보다 크면 ping 보냄
    todo
    '''
    def __init__(self) -> None:
        pass