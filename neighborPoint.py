import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from datetime import datetime


def prevPointCalc(center_latitude, center_longitude, cur_latitude, cur_longitude, unit):
    '''
    
    본 함수는 현재의 좌표점에서 중심점, GCS의 위치로 가기 위한 바로 이전의 지점의 위치를 구함

    input : 위도, 경도로 구성된 2개의 점. 각각 시작점, 종료점임. 좌표는 소수점 5자리까지로 표현
    center_longitude, center_latitude : 중심점, GCS의 위치에 해당하는 좌표의 위도와 경도
    cur_longitude, cur_latitude : 현재 지점의 위도와 경도

    output : 원의 중심점, GCS와 현재 지점을 연결하는 직선 위 픽셀 중 현재 지점과 가장 
    가까운 픽셀의 좌표값의 위도, 경도. 소수점 5자리로 표현    
    '''

    if center_latitude == cur_latitude: # 같은 위도의 점에서
        if center_longitude == cur_longitude: # 경도가 동일
            # 시작점과 종료점이 같은 경우 None 반환
            return None
        elif center_longitude > cur_longitude: # 현재 지점이 중심보다 경도가 작음
            return center_latitude, round(cur_longitude + unit*0.00001, 5)
        elif center_longitude < cur_longitude: # 현재 지점이 중심보다 경도가 큼
            return center_latitude, round(cur_longitude - unit*0.00001, 5)

    else: # 위도가 다른 경우
        if center_longitude == cur_longitude: # 경도는 동일
            if center_latitude > cur_latitude:
                return round(cur_latitude + unit*0.00001, 5), center_longitude
            elif center_latitude < cur_latitude:
                return round(cur_latitude - unit*0.00001, 5), center_longitude
        else:
            return _calcPrevPoint(cur_longitude, cur_latitude, center_longitude, center_latitude, unit)

def _calcPrevPoint(start_longitude, start_latitude, end_longitude, end_latitude, unit):

    
    # 경도, x
    delta_lng = end_longitude - start_longitude

    # 위도, y 
    delta_lat = end_latitude - start_latitude 

    angle = math.degrees(math.atan2(delta_lat, delta_lng)) % 360

    if angle < 18:
        # 우측 픽셀 반환
        return start_latitude, round(start_longitude + unit*0.00001, 5)
    elif angle < 68:
        # 우측 상단 픽셀 반환
        return round(start_latitude + unit*0.00001, 5), round(start_longitude + unit*0.00001, 5)
    elif angle < 112:
        # 상단 픽셀 반환
        return round(start_latitude + unit*0.00001, 5), start_longitude
    elif angle < 161:
        # 상단 좌측 픽셀 반환
        return round(start_latitude + unit*0.00001, 5), round(start_longitude - unit*0.00001, 5)
    elif angle < 199:
        # 좌측 픽셀 반환
        return start_latitude, round(start_longitude - unit*0.00001, 5)
    elif angle < 248:
        # 좌측 하단 픽셀 반환
        return round(start_latitude - unit*0.00001, 5), round(start_longitude - unit*0.00001, 5)
    elif angle < 292:
        # 하단 픽셀 반환
        return round(start_latitude - unit*0.00001, 5), start_longitude
    elif angle < 342:
        # 하단 우측 픽셀 반환
        return round(start_latitude - unit*0.00001, 5), round(start_longitude + unit*0.00001, 5) 
    else:
        # 우측 픽셀 반환
        return start_latitude, round(start_longitude + unit*0.00001, 5)

def circularSearch(start_latitude, start_longitude, layer):
    '''
    시작지점을 기준으로 반시계 방향으로 각 layer를 탐색
    지점 정보가 저장되어 있지 않은 경우 크롤링
    '''
    latitude_points = []
    longitude_points = []

    cur_layer = 1   
    while layer > cur_layer:

        for displace in range(-cur_layer, cur_layer):
            # 좌측 변, 상향
            longitude_points.append(round(start_longitude - cur_layer*0.00001, 5))
            latitude_points.append(round(start_latitude + displace*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 윗쪽 변, 우향
            longitude_points.append(round(start_longitude + displace*0.00001, 5))
            latitude_points.append(round(start_latitude + cur_layer*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 우측 변, 상향
            longitude_points.append(round(start_longitude + cur_layer*0.00001, 5))
            latitude_points.append(round(start_latitude - displace*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 밑쪽 변, 우향
            longitude_points.append(round(start_longitude - displace*0.00001, 5))
            latitude_points.append(round(start_latitude - cur_layer*0.00001, 5))

        cur_layer += 1

    return latitude_points, longitude_points

def circularSearchUnit(start_latitude, start_longitude, layer, unit=1):
    '''
    시작지점을 기준으로 반시계 방향으로 각 layer를 탐색
    지점 정보가 저장되어 있지 않은 경우 크롤링
    start_latitude : 탐색 시작 지점 위도
    start_longitude : 탐색 시작 지점 경도
    layer : 시작 지점을 포함하여 모서리까지의 픽셀 개수 (3*3 정사각형의 layer는 2)
    unit : 탐색하고자 하는 픽셀의 단위, 시작 지점에서 n 만큼 떨어진 픽셀 탐색 시작
    '''
    latitude_points = []
    longitude_points = []

    cur_layer = 1   
    while layer > cur_layer:

        for displace in range(-cur_layer, cur_layer):
            # 좌측 변, 상향
            longitude_points.append(round(start_longitude - unit*cur_layer*0.00001, 5))
            latitude_points.append(round(start_latitude + unit*displace*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 윗쪽 변, 우향
            longitude_points.append(round(start_longitude + unit*displace*0.00001, 5))
            latitude_points.append(round(start_latitude + unit*cur_layer*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 우측 변, 상향
            longitude_points.append(round(start_longitude + unit*cur_layer*0.00001, 5))
            latitude_points.append(round(start_latitude - unit*displace*0.00001, 5))
        for displace in range(-cur_layer, cur_layer):
            # 밑쪽 변, 우향
            longitude_points.append(round(start_longitude - unit*displace*0.00001, 5))
            latitude_points.append(round(start_latitude - unit*cur_layer*0.00001, 5))

        cur_layer += 1

    return latitude_points, longitude_points

class PointData:
    def __init__(self, layer, center_latitude, center_longitude, unit) -> None:
        '''
        layer는 중심점 픽셀부터 사각형의 한 변의 중심점 픽셀까지의 픽셀 개수임
        위도 및 경도 값은 십의 -5자리까지 표시되는 정수임
        point_data는 각 지점의 정보를 포함함
        '''
        self.layer = layer
        self.center_latitude = center_latitude
        self.center_longitude = center_longitude
        self.unit = unit
        self.point_Data = self._getEmptyList(layer)

    def _getEmptyList(self, layer):
        '''
        고도 정보 저장을 위한 2차원 리스트 반환
        layer는 중심점 픽셀부터 사각형의 한 변의 중심점 픽셀까지의 픽셀 개수임
        3*3 리스트의 layer는 2
        2차원 리스트는 정사각형 형태임
        '''
        return [[None for _ in range(layer*2-1)] for i in range(layer*2-1)]
    
    def _getIndex(self, latitude, longitude):
        lat_idx = int(round(latitude*100000, 0)) - int(round(self.center_latitude*100000, 0)) + self.layer - 1
        lng_idx = int(round(longitude*100000, 0)) - int(round(self.center_longitude*100000, 0)) + self.layer - 1

        lat_idx = lat_idx//self.unit
        lng_idx = lng_idx//self.unit
        
        # print(self.center_latitude, self.center_longitude, latitude, longitude, lat_idx, lng_idx)
        return lat_idx, lng_idx
    
    def getData(self, latitude, longitude):
        lat_idx, lng_idx = self._getIndex(latitude, longitude)
        return self.point_Data[lat_idx][lng_idx]
    
    def setData(self, latitude, longitude, slope):
        lat_idx, lng_idx = self._getIndex(latitude, longitude)
        self.point_Data[lat_idx][lng_idx] = slope

def _show_scatterAni(x_points, y_points):

    fig, ax = plt.subplots()
    ax.set_ylim(35.0 - 0.0002, 35.0 + 0.0002)
    ax.set_xlim(126.0  - 0.0002, 126.0 + 0.0002)
    scatter = ax.scatter([], [])

    def animate(frame):
        scatter.set_offsets(np.column_stack((x_points[:frame+1], y_points[:frame+1])))
        return scatter,

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        return scatter,

    ani = FuncAnimation(fig, animate, frames=len(y_points), init_func=init, blit=True)
    ani.save(f'scatter_animation_{str(datetime.now().timestamp())}.gif', writer='imagemagick')

    plt.show()

def _show_lineAni(start_x, start_y, x_points, y_points):

    def init():
        line.set_data([], [])
        return line,


    def animate(frame):
        if frame == 0:
            return init()
        x = []
        y = []
        for p in x_points[:frame+1]:
            x.append(start_x)
            x.append(p)
        for p in y_points[:frame+1]:
            y.append(start_y)
            y.append(p)
        print(x,y)
        line.set_data(x,y)

        return line,
    
    fig, ax = plt.subplots()
    ax.set_ylim(35.0 - 0.0002, 35.0 + 0.0002)
    ax.set_xlim(126.0  - 0.0002, 126.0 + 0.0002)
    line, = ax.plot([], [], color='r')

    ani = FuncAnimation(fig, animate, frames=len(y_points), init_func=init, blit=True)
    ani.save(f'scatter_animation_{str(datetime.now().timestamp())}.gif', writer='imagemagick')

    plt.show()

def _show_lineScatterAni(start_x, start_y, x_points, y_points):

    def init():
        line.set_data([], [])
        return line,


    def animate(frame):
        if frame == 0:
            return init()
        x = []
        y = []
        for p in x_points[:frame+1]:
            x.append(start_x)
            x.append(p)
        for p in y_points[:frame+1]:
            y.append(start_y)
            y.append(p)
        print(x,y)
        line.set_data(x,y)

        scatter_now.set_offsets(np.column_stack((x_points[frame], y_points[frame])))

        scatter_cur.set_offsets(np.column_stack((x_points[:frame+1], y_points[:frame+1])))

        scatter_prev.set_offsets(np.column_stack((prev_lng[frame], prev_lat[frame])))

        text.set_text(f'center : {start_x}, {start_y} / cur : {x_points[frame]}, {y_points[frame]}, prev : {prev_lng[frame]}, {prev_lat[frame]}')

        return line, scatter_cur, scatter_prev, text, scatter_now
    
    
    fig, ax = plt.subplots(figsize=(16, 16))
    text = ax.text(126.0 - 0.00018, 35.0 + 0.00018, '', ha='left', va='center', fontsize=7)
    ax.set_ylim(35.0 - 0.0002, 35.0 + 0.0002)
    ax.set_xlim(126.0  - 0.0002, 126.0 + 0.0002)
    
    scatter_cur = ax.scatter([], [], color='r', zorder=1, label='old')
    line, = ax.plot([], [], color='r', zorder=2)
    scatter_prev = ax.scatter([], [], color='b', zorder=3, label='prev')
    scatter_now = ax.scatter([], [], color='yellow', zorder=4, label='now')

    ax.legend()
    
    prev_lat = []
    prev_lng = []

    for i in range(len(x_points)):
        lat, lng = prevPointCalc(start_y, start_x, y_points[i], x_points[i])
        prev_lat.append(lat)
        prev_lng.append(lng)
        # print(start_y, start_x, y_points[i], x_points[i], lat, lng)

    ani = FuncAnimation(fig, animate, frames=len(y_points), init_func=init, blit=True, interval=1000/1)
    ani.save(f'scatter_animation_{str(datetime.now().timestamp())}.gif', writer='imagemagick')

    plt.show()
    
def _test_circularSearch():

    # latitude_points, longitude_points = circularSearch(35.0, 126.0, 10)

    latitude_points, longitude_points = circularSearchUnit(35.0, 126.0, 30, 2)

    _show_scatterAni(longitude_points, latitude_points)

def _test_lineAlg():

    latitude_points, longitude_points = circularSearch(35.0, 126.0, 10)

    _show_lineAni(126.0, 35.0, longitude_points, latitude_points)

def _test_lineScattAlg():

    latitude_points, longitude_points = circularSearch(35.0, 126.0, 10)

    _show_lineScatterAni(126.0, 35.0, longitude_points, latitude_points)

    

if __name__ =='__main__':
    # for i in range(10000):
    #     print(prevPointCalc(0.0, 0.0, 1.0, 1.0))
    #print(prevPointCalc(35.1681,128.0978, 35.16809, 128.09781))

    # slope = SlopeData(5, 126.0, 126.0)
    
    # print(prevPointCalc(35.1681,128.0978, 35.16809, 128.09781))

    # _test_circularSearch()
    # _test_lineAlg()
    # _test_lineScattAlg()
    # print(prevPointCalc(35.0, 126.0, 34.99991, 126.00003))

    # slopeData = SlopeData(15, 35.15638, 128.07373)
    # print(len(slopeData.point_Data))
    # print(slopeData.getData(35.15638, 128.07373))
    # slopeData.setSlope(35.15638, 128.07373, 10)

    # slopeData.setSlope(35.15638, 128.07374, 9)
    # slopeData.setSlope(35.15639, 128.07374, 9)
    # slopeData.setSlope(35.15639, 128.07373, 9)
    # slopeData.setSlope(35.15638, 128.07372, 9)
    # slopeData.setSlope(35.15639, 128.07372, 9)
    # slopeData.setSlope(35.15637, 128.07373, 9)
    # slopeData.setSlope(35.15637, 128.07372, 9)
    # slopeData.setSlope(35.15638, 128.07372, 9)


    # print(slopeData.getData(35.15638, 128.07373))
    _test_circularSearch()
