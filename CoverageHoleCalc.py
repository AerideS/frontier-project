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

JUMP_GAP = 0.00002
CLOSE_GAP = 0.00003
APPEND_THRESHOLD_LENGTH = 20

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
        # print(slopeData.getData(35.15638, 128.07373))``
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

    min_lat = gcs_lat - distance*unit*0.00001
    min_lng = gcs_lng - distance*unit*0.00001
    max_lat = gcs_lat + distance*unit*0.00001
    max_lng = gcs_lng + distance*unit*0.00001

    # for i, single_points in enumerate(losDifData.point_Data):
    #     for j, single_point in enumerate(single_points):
    
    losDifData = losDif.point_Data

    # print(losDifData)
    # input()8
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
    
    # def nearest_neighbor_sort(points):
    #     points = np.array(data)
    #     remaining = points.tolist()
    #     sorted_points = [remaining.pop(0)]
        
    #     while remaining:
    #         last_point = sorted_points[-1]
    #         distances = [distance.euclidean(last_point, point) for point in remaining]
    #         nearest_index = np.argmin(distances)
    #         sorted_points.append(remaining.pop(nearest_index))
        
    #     return np.array(sorted_points)
    
    def coordRevert(lat, lng):
        coord_x = int(round((lng - gcs_lng)*100000 / unit, 5))
        coord_y = int(round((lat - gcs_lat)*100000 / unit, 5))

        return coord_x, coord_y
    
    def visualize_groups(groups):
        plt.figure(figsize=(14,14))
        plt.xlim(gcs_lng - distance*unit*0.00001, gcs_lng + distance*unit*0.00001)
        plt.ylim(gcs_lat - distance*unit*0.00001, gcs_lat + distance*unit*0.00001)
        plt.scatter(gcs_lng, gcs_lat, c='r')

        lat_points = None
        lng_points = None

        if type(groups[0]) == list:
            for point_list in groups:
                lng_points = [point[0] for point in point_list]
                lat_points = [point[1] for point in point_list]                

                plt.scatter(lng_points, lat_points)
        
        else:         

            lat_points = [point[1] for point in groups]
            lng_points = [point[0] for point in groups]
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
    
    def visualize_groups_animation(result):

        new_result = []
        for point in result:
            new_result += point

        print(result)
        # new_result = new_result[0]
        fig, ax = plt.subplots()
        scat = ax.scatter([], [])

        print('new_result', new_result)
        # plt.figure(figsize=(14,14))
        plt.xlabel('Latitude (deg)', fontsize=8)
        plt.ylabel('Longitude (deg)', fontsize=8)
        plt.xlim(gcs_lng - distance*unit*0.00001, gcs_lng + distance*unit*0.00001)
        plt.ylim(gcs_lat - distance*unit*0.00001, gcs_lat + distance*unit*0.00001)
        plt.xticks(fontsize=12)
        current_values = plt.gca().get_xticks()
        plt.gca().set_xticklabels(['{:.5f}'.format(x) for x in current_values])
        plt.yticks(fontsize=12)
        current_values = plt.gca().get_yticks()
        plt.gca().set_yticklabels(['{:.5f}'.format(x) for x in current_values])

        def update(frame):
            current_data = new_result[:frame + 1]
            x_data = [point[0] for point in current_data]
            y_data = [point[1] for point in current_data]
            # print(x_data, y_data)
            # if frame > 2:
                # print(distance_calc((x_data[-1], y_data[-1]), (x_data[-2], y_data[-2]) ))
            scat.set_offsets(np.column_stack((x_data, y_data)))
            return scat,

        ani = FuncAnimation(fig, update, frames=range(len(new_result)), interval=50)
        ani.save(f'./polygone/hole_polygone_{lat}_{lng}_{alt}__{unit}_{str(datetime.now().timestamp())}.gif')
        plt.show()
        
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

    def distance_calc(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def get_sorted(points : list): #key=lambda p: distance_calc(p, last_point)
        left_lower = min(points, key=lambda p: distance_calc(p, (min_lng, min_lat)))
        left_upper = min(points, key=lambda p: distance_calc(p, (min_lng, max_lat)))
        right_lower = min(points, key=lambda p: distance_calc(p, (max_lng, min_lat)))
        right_upper = min(points, key=lambda p: distance_calc(p, (max_lng, max_lat)))

        # gap_lst = [round(cur_min_lng_pnt[0] - min_lng, 5), round(max_lng - cur_max_lng_pnt[0], 5),
        #            round(cur_min_lat_pnt[1] - min_lat, 5), round(max_lat - cur_max_lat_pnt[1], 5)]
        
        gap_lst = [distance_calc(left_lower, (min_lng, min_lat)), distance_calc(left_upper, (min_lng, max_lat)),
                   distance_calc(right_lower, (max_lng, min_lat)), distance_calc(right_upper, (max_lng, max_lat))]
        
        print(gap_lst)

        min_gap = min(gap_lst)

        if min_gap == gap_lst[0]:
            return left_lower
        elif min_gap == gap_lst[1]:
            return left_upper
        elif min_gap == gap_lst[2]:
            return right_lower
        elif min_gap == gap_lst[3]:
            return right_upper

    def seperate_points_list(points: list):
        # todo: 경도 손 정렬 --> 가장 작은거를 pop해서 시작점으로
        print(points)
        sorted_points_list = []

        sorted_points = [get_sorted(points)]
        points.remove(sorted_points[0])

        # sorted_points := [points.pop(0)] # 임의의 시작점 (여기서는 첫 번째 점)
        while points:
            last_point = sorted_points[-1]
            next_point = min(points, key=lambda p: distance_calc(p, last_point))

            dist = distance_calc(last_point, next_point)
            if dist > JUMP_GAP:
                # 다음 지점이 일정 거리 이상 지점인 경우 새로운 목록 생성
                print(dist)
                sorted_points_list.append(sorted_points)
                sorted_points = [get_sorted(points)]
                print('next_point', next_point)
            else:
                sorted_points.append(next_point)
                points.remove(next_point)
                

        sorted_points_list.append(sorted_points)

        return sorted_points_list
    

    def seperate_points(points : list):
        #todo 경도 순 정렬 -> 가장 작은거를 pop 해서 시작점으로

        sorted_points = [get_sorted(points)]

        points.remove(sorted_points[0])

        # sorted_points = [points.pop(0)]  # 임의의 시작점 (여기서는 첫 번째 점)
        while points:
            last_point = sorted_points[-1]
            next_point = min(points, key=lambda p: distance_calc(p, last_point))

            dist = distance_calc(last_point, next_point) 
            if dist > JUMP_GAP:
                print(dist)
                next_point = get_sorted(points)
                print('next_point', next_point)

            points.remove(next_point)
            sorted_points.append(next_point)


        return sorted_points
    
    def sort_direction(lines):
        pass

    def mergeLines(line_list):
        merged_lines = []
        for single_line in line_list:
            merged_lines += single_line

        return merged_lines
    
    def sort_line_order(lines : list):

        node = []
        new_lines = []
        for i in lines:
            print(i[0], i[-1])
            node.append((i[0], i[-1]))

        print(lines, '-------------------')

        while True:
            new_lines = [lines.pop()]
            print('new_lines', new_lines)
            node.pop()
            if len(new_lines[0]) > APPEND_THRESHOLD_LENGTH:
                break


        while lines:
            min_dist = float('INF')
            min_dist_index = None
            print('-------------')

            for i, single_node in enumerate(node):
                print(new_lines, single_node)
                first_dist = distance_calc(new_lines[-1][-1], single_node[0])    # 현재 지점의 시작점, 이전 지점의 시작점
                second_dist = distance_calc(new_lines[0][0], single_node[0])   # 현재 지점의 시작점, 이전 지점의 종료점

                third_dist = distance_calc(new_lines[-1][-1], single_node[1])    # 현재 지점의 종료점, 이전 지점의 시작점
                fourth_dist = distance_calc(new_lines[0][0], single_node[1])   # 현재 지점의 종료점, 이전 지점의 시작점

                if  first_dist < min_dist:
                    min_dist_index = (i, 0)
                    min_dist = first_dist

                if  second_dist < min_dist:
                    min_dist_index = (i, 1)
                    min_dist = second_dist

                if  third_dist < min_dist:
                    min_dist_index = (i, 2)
                    min_dist = third_dist

                if  fourth_dist < min_dist:
                    min_dist_index = (i, 3)
                    min_dist = fourth_dist
            
            print(min_dist_index, 449)

            if len(lines[min_dist_index[0]]) < APPEND_THRESHOLD_LENGTH:
                print(new_lines)
                lines.pop(min_dist_index[0])
                print(new_lines)
            elif min_dist_index[1] == 0:
                print(new_lines)
                new_lines += [lines.pop(min_dist_index[0])]
                print(new_lines)
            elif min_dist_index[1] == 1:
                print(new_lines)
                new_lines = [list(reversed(lines.pop(min_dist_index[0])))] + new_lines
                print(new_lines)
            elif min_dist_index[1] == 2:
                print(new_lines)
                new_lines += [list(reversed(lines.pop(min_dist_index[0])))]
                print(new_lines)
            elif min_dist_index[1] == 3:
                print(new_lines)
                new_lines = [lines.pop(min_dist_index[0])] + new_lines
                print(new_lines)

            node.pop(min_dist_index[0])

        return new_lines

    def get_degree(point):
        '''
        꼭지점 대비 시작점의 위치 구하기
        정사각형의 각 꼭지점과 중심점을 기준으로 지점이 어느 위치에 있는지 반환
        -------------
        | \   0   / |
        |   \   /   |
        | 1   X   3 |
        |   /   \   |
        | /   2   \ |
        -------------                   
        각 지점에 해당하는 숫자 반환
        '''
        angle = math.atan((point[1] - gcs_lat) /  (point[0] - gcs_lng))

        return angle
        # if (angle >= 0.7854) and (angle <= 2.3562):
        #     return 0
        # elif (angle >= 2.3562) and (angle <= 3.9270):
        #     return 1
        # elif (angle >= 3.9270) and (angle <=  5.4978):
        #     return 2
        # elif (angle >=  5.4978) or (angle <= 0.7854):
        #     return 3      

    def add_vertex(lines):
        '''
        각 지점에 선 단위로 각도 얻어냄 -> 회전 방향 알아냄 : 시계, 반시계
        
        다음 선으로 이동할 때, 모서리가 뛰는 경우 점 추가

            모서리가 뛰지 않는 경우 넘기기

        끝난 경우 시작 지점 사이에 모서리 추가

        '''
        for single_line in lines:
            rotate_angle = 0
            for i in range(len(single_line)-2):
                rotate_angle += (get_degree(single_line[i]) - get_degree(single_line[i+1]))

            # if rotate_angle



    def process_result(result):
        '''
        근접하는 선들을 연결
        '''

        lines = mergeLines(result) # 선들을 하나의 목록으로 통합

        # visualize_groups(lines)
        
        # seperated_lines = seperate_points(lines) # 점들을 분할

        print('seperated_lines', lines)

        # visualize_groups(lines)

        lines = sort_line_order(lines)

        visualize_groups(lines)

        # lines = add_vertex(lines)

        return lines
    
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
            if visited[cx][cy]:
                continue
            visited[cx][cy] = True
            if has_adjacent(cx, cy):
                group.append(coordConvert(cx,cy))
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if is_valid(nx, ny):
                    if losDifData[nx][ny] is None:
                        stack.append((nx, ny))
                    elif (not visited[nx][ny] and losDifData[nx][ny] > 0):
                        stack.append((nx, ny))

        return group


    for i in range(rows):
        for j in range(cols):
            if (losDifData[i][j] is not None):
                # 통신 가능 지점에서 탐색 시작
                if (losDifData[i][j] > 0) and (not visited[i][j]): 
                    group = dfs(i, j)
                    if group:
                        # group = addAdditonPoint(group)
                        result.append(seperate_points_list(group))

    # print(visited)
    print(result)
    # visualize_groups(result)
    result = process_result(result)
    # print(len(result))
    visualize_groups(result)
    print("making animation")
    visualize_groups_animation(result)
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
    # lat = 35.15992
    # lng = 128.08762
    # showGraph(lat, lng, alt, 1, 1, distane=distance)
    polygone = getPolygone(lat, lng, alt, 1, 1, distance)
    # visualize_matrix(distance, polygone)


