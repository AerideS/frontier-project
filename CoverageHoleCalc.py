from neighborPoint import *
# from mongodb_api import *
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
# from elevation_crawling import *
from elevationData import * 
from matplotlib.animation import FuncAnimation

import math

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

terrain_data = FileToAlt()

def calculate_diagonal_length(start_lat, start_lng, end_lat, end_lng):
    '''
    특정 두 지점 사이의 거리를 계산함
    '''
    return math.sqrt(abs(start_lat-end_lat)**2 + abs(start_lng-end_lng)**2)


def calculationLos(gcs_latitude, gcs_longitude, gcs_altitude, unit = 1, flight_alt = None, distance = 90):
    # GCS에서 각 지점까지 직선의 기울기를 포함함
    slopeData = PointData(distance, gcs_latitude, gcs_longitude, unit)
    # 통신가능최소고도. 지형에 의해 각 지점에 통신이 가능한 최소 고도를 포함함
    losData = PointData(distance, gcs_latitude, gcs_longitude, unit)
    # 드론 비행고도 - 통신가능최소고도 : 드론이 지표면 위의 특정 고도에서 비행할때, 통신가능최소고도 대비 고도
    # Critical : 고도는 지표 대비 상대 고도임!
    losDifData = PointData(distance, gcs_latitude, gcs_longitude, unit)
    slopeData.setData(gcs_latitude, gcs_longitude, float('-INF'))

    gcs_height = terrain_data.getHeight(gcs_latitude, gcs_longitude) + gcs_altitude

    # print(gcs_latitude, gcs_longitude, distance, unit)
    latitude_points, longitude_points = circularSearchUnit(gcs_latitude, gcs_longitude, distance, unit)
    # print(latitude_points, longitude_points)

    for i in range(len(latitude_points)):
        
        cur_lat = latitude_points[i]
        cur_lng = longitude_points[i]
        cur_height = terrain_data.getHeight(cur_lat, cur_lng)

        #현재 지점에서 GCS로 향하는 근접 픽셀의 위도와 경도 (이전지점) 
        prev_lat, prev_lng = prevPointCalc(gcs_latitude, gcs_longitude, 
                                           cur_lat, cur_lng, unit)
        
        #현재 지점과 GCS 사이의 거리 계산
        distance_to_gsc =  calculate_diagonal_length(cur_lat, cur_lng, gcs_latitude, gcs_longitude)

        #현재지점과 중심점(GCS위치) 사이의 고도차 계산
        elev_diff_gsc = cur_height - gcs_height


        cur_slope = elev_diff_gsc/distance_to_gsc
        prev_slope = slopeData.getData(prev_lat, prev_lng)

        max_slope = max(cur_slope, prev_slope)
        slopeData.setData(cur_lat, cur_lng, max_slope)
        los_Height = gcs_height + max_slope*distance_to_gsc

        losData.setData(cur_lat, cur_lng, los_Height)
        # print('way', cur_lat, cur_lng, cur_height, los_Height, flight_alt)

        losDifData.setData(cur_lat, cur_lng, cur_height - los_Height + flight_alt)

        if los_Height == None:
            print(None)
            # print('cur', cur_lat, cur_lng, cur_height, cur_slope, 'prv', prev_lat, prev_lng, prev_slope, 'gcs', gcs_latitude, gcs_longitude, gcs_height, distance_to_gsc, 'result', max_slope, los_Height)

        # print('cur', cur_lat, cur_lng, cur_height, cur_slope, 'prv', prev_lat, prev_lng, prev_slope, 'gcs', gcs_latitude, gcs_longitude, gcs_height, distance_to_gsc, 'result', max_slope, los_Height)

    losDifData.setData(gcs_latitude, gcs_longitude, float('INF'))

    return losData, losDifData 


def calculation(ax, gcs_latitude, gcs_longitude, gcs_altitude, unit = 1, distance = 30):
    slopeData = PointData(distance, gcs_latitude, gcs_longitude, unit)
    losData = PointData(distance, gcs_latitude, gcs_longitude, unit)
    slopeData.setData(gcs_latitude, gcs_longitude, float('-INF'))
    gcs_height = terrain_data.getHeight(gcs_latitude, gcs_longitude) + gcs_altitude
    latitude_points, longitude_points = circularSearchUnit(gcs_latitude, gcs_longitude, distance, unit)
    # print('latitude_points', latitude_points)
    ax.scatter(gcs_latitude, gcs_longitude, gcs_height, c='r')

    for i in range(len(latitude_points)):
        
        cur_lat = latitude_points[i]
        cur_lng = longitude_points[i]
        cur_height = terrain_data.getHeight(cur_lat, cur_lng)

        #현재 지점에서 GCS로 향하는 근접 픽셀의 위도와 경도 (이전지점) 
        prev_lat, prev_lng = prevPointCalc(gcs_latitude, gcs_longitude, cur_lat, cur_lng, unit)
        
        #현재 지점과 GCS 사이의 거리 계산
        distance_to_gsc =  calculate_diagonal_length(cur_lat, cur_lng, gcs_latitude, gcs_longitude)

        #현재지점과 중심점(GCS위치) 사이의 고도차 계산
        elev_diff_gsc = cur_height - gcs_height


        cur_slope = elev_diff_gsc/distance_to_gsc
        # print(slopeData.getData(35.15638, 128.07373))
        prev_slope = slopeData.getData(prev_lat, prev_lng)
        # print(slopeData.getData(35.15638, 128.07373))
        # print(cur_slope, prev_slope)

        max_slope = max(cur_slope, prev_slope)
        # print(slopeData.getData(35.15638, 128.07373))
        slopeData.setData(cur_lat, cur_lng, max_slope)
        # print(slopeData.getData(35.15638, 128.07373))
        los_Height = gcs_height + max_slope*distance_to_gsc

        ax.scatter(cur_lat, cur_lng, los_Height, c='b')

        ax.scatter(cur_lat, cur_lng, cur_height, c='g')


        losData.setData(cur_lat, cur_lng, los_Height)

        # print('cur', cur_lat, cur_lng, cur_height, cur_slope, 'prv', prev_lat, prev_lng, prev_slope, 'gcs', gcs_latitude, gcs_longitude, gcs_height, distance_to_gsc, 'result', max_slope, los_Height)
        
def showGraph(gcs_lat, gcs_lng, gcs_alt, unit, drone_alt, distane):
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    for alt in range(1,11):
        print('calc start', alt)
        calculation(ax, gcs_lat, gcs_lng, gcs_alt, unit)
        print('calc complete', alt)
        plt.xlabel('Latitude (deg)', fontsize=8)
        plt.ylabel('Longitude (deg)', fontsize=8)
        # plt.zlabel('Elevation (m)', fontsize=24)
        plt.xticks(fontsize=12)
        current_values = plt.gca().get_xticks()
        plt.gca().set_xticklabels(['{:.5f}'.format(x) for x in current_values])
        plt.yticks(fontsize=12)
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:.5f}'.format(x) for x in current_values])

        def update(frame):
            # 각 프레임마다 그래프를 회전시킵니다.
            ax.view_init(elev=20, azim=frame)
        # plt.show()
        print('making animation')
        ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=50)
        ani.save(f'./3d_hole/3d_hole_calculation_{lat}_{lng}_{alt}__{unit}_{str(datetime.now().timestamp())}.gif')
        # plt.show()
        plt.cla()

def getPolygone(gcs_lat, gcs_lng, gcs_alt, unit, drone_alt, distance):
    '''
    특정 GCS 위치에서의 음영지역에 대한 폴리곤 return
    gcs_lat : GCS의 위도
    gcs_lng : GCS의 경도  
    gcs_alt : unit
    drone_alt : 드론이 비행할 고도, 
        지표면 대비 해당 고도보다 통신가능최소고도가 높은 경우 해당 지역을 음영지역이라 
        간주하고 해당 지역에 폴리곤을 생성함
    '''

    los, losDif = calculationLos(gcs_latitude=gcs_lat, gcs_longitude=gcs_lng, 
                                         gcs_altitude=gcs_alt, unit=unit, flight_alt=drone_alt, distance=distance)


    # for i, single_points in enumerate(losDifData.point_Data):
    #     for j, single_point in enumerate(single_points):
    
    losDifData = losDif.point_Data

    # print(losDifData)
    # input()
    if not losDifData:
        return []

    rows, cols = len(losDifData), len(losDifData[0])
    visited = [[False] * cols for _ in range(rows)]
    result = []
    # directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def is_valid(x, y):
        return 0 <= x < rows and 0 <= y < cols
    
    def is_visited(x, y):
        return visited[x,y]
    
    def coordConvert(lat, lng):
        real_lat = round(gcs_lat + (lat - distance + 1) * 0.00001 * unit, 5)
        real_lng = round(gcs_lng + (lng - distance + 1) * 0.00001 * unit, 5)

        return (real_lng, real_lat)
    
    def coordRevert(lat, lng):
        coord_x = int(round((lng - gcs_lng)*100000 / unit, 5))
        coord_y = int(round((lat - gcs_lat)*100000 / unit, 5))

        return coord_x, coord_y
    
    def visualize_groups(groups):
        plt.figure(figsize=(14,14))
        plt.xlim(gcs_lng - distance*unit*0.00001, gcs_lng + distance*unit*0.00001)
        plt.ylim(gcs_lat - distance*unit*0.00001, gcs_lat + distance*unit*0.00001)
        plt.scatter(gcs_lng, gcs_lat, c='r')

        for point_list in groups:
            lat_points = [point[1] for point in point_list]
            lng_points = [point[0] for point in point_list]
            plt.scatter(lng_points, lat_points)

        plt.xticks(fontsize=18)
        current_values = plt.gca().get_xticks()
        plt.gca().set_xticklabels(['{:.5f}'.format(x) for x in current_values])
        plt.yticks(fontsize=18)
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:.5f}'.format(x) for x in current_values])
        
        plt.grid(True, which='both', color='gray', linewidth=0.5, linestyle='--')
        plt.xlabel('Longitude(deg)', fontsize=18)
        plt.ylabel('Latitude(deg)', fontsize=18)
        
        plt.savefig(f'./polygone/polygoneFinder_{gcs_lat}_{gcs_lng}_{gcs_alt}__{str(datetime.now().timestamp())}.png')
        plt.show()
    
    def addAdditonPoint(group):
        GAP = 0.00002
        start_point = group[0]
        end_point = group[-1]

        lng_gap = start_point[0] - end_point[0]
        lat_gap = start_point[1] - end_point[1]

        if -GAP < lng_gap < GAP :
            return group
        if -GAP < lat_gap < GAP :
            return group  
        
    def has_adjacent(x, y):
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                if losDifData[nx][ny] is None: # None MEANS GCS POINT!
                    return False
                elif losDifData[nx][ny] < 0:
                    return True
        return False
    
    def get_neighbor(x, y):
        return [(x-1, y), (x-1, y-1), (x, y-1), (x+1, y), (x+1, y+1), (x+1, y-1), (x, y+1), (x+1, y+1)]

    def dfs(x, y):
        '''
        0보다 작은 지점에 대해 시작
        이웃 중 0보다 작은 지점이 있으면 group에 추가 
        추가한 지점과 현재 지점에 대해 공통되는 이웃 중 0보다 큰 지점을 다음 방문 지점 stack에 추가
        '''
        stack = [(x, y)]
        group = []
        while stack:
            cx, cy = stack.pop() 
            if visited[cx][cy]: # 방문한 경우 pass
                continue
            visited[cx][cy] = True

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy # 다음 지점 nx, ny
                if is_valid(nx, ny): 
                    if losDifData[nx][ny] > 0: # 통신 가능한 지점인 경우
                        group.append(coordConvert(nx, ny)) # 목록에 추가

                        nxt_pnt_nei = get_neighbor(nx, ny) # 통신 가능 지점의 이웃 지점들
                        cur_pnt_nei = get_neighbor(cx, cy) # 현재 지점의 이웃 지점들
                        
                        # 두 지점들이 겹치는 경우에 대해 
                        common_pnt = [point for point in nxt_pnt_nei if point in cur_pnt_nei]

                        for s_p in common_pnt:
                            if is_valid(s_p[0], s_p[1]) is False:
                                continue
                            elif losDifData[s_p[0]][s_p[1]] < 0:
                                stack.append((s_p[0], s_p[1]))

            # print(stack)
            

        return group


    for i in range(rows):
        for j in range(cols):
            if (losDifData[i][j] is not None):
                # 통신 가능 지점에서 탐색 시작
                if (losDifData[i][j] < 0) and (not visited[i][j]): 
                    group = dfs(i, j)
                    if group:
                        # group = addAdditonPoint(group)
                        result.append(group)

    # print(visited)
 
    print(result)
    visualize_groups(result)
    return result
  
if __name__ == '__main__':
    #crawlingInList([35.16810], [128.09780])
    # calculation(35.16810, 128.09780)
    # calculation(35.16710, 128.09780)
    # calculation(35.14682, 128.06645)
    # calculation(35.14773, 128.06539) # 오류
    # calculation(35.14809, 128.06525) 35.156386°N 128.073739°E
    # calculation(35.15638, 128.07373)
    # calculation(35.15162, 128.08432) #35.151623°N 128.084322°E
    # 
    # case 1----------------------------
    # lat = 35.16223
    # lng = 128.08989
    alt = 1.0    
    distance = 90
    unit = 1
    # case 2----------------------------
    lat = 35.16258
    lng = 128.09260
    # case 3----------------------------
    lat = 35.15992
    lng = 128.08762
    # showGraph(lat, lng, alt, 1, 1, distane=distance)
    polygone = getPolygone(lat, lng, alt, 1, 1, distance)
    # visualize_matrix(distance, polygone)


