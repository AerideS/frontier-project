import math

def generate_circle_points(center, radius, num_points=100):
    points = []
    h, k = center
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points  # 0부터 2π까지의 각도를 num_points로 나누어 계산
        x = round(h + radius * math.cos(angle), 5)
        y = round(k + radius * math.sin(angle), 5)
        points.append((x, y))
    return points

gcs_lng = 128.0
gcs_lat = 35.0

print(generate_circle_points((gcs_lng, gcs_lat), 0.001))
def get_degree(point):
    '''
    꼭지점 대비 시작점의 위치 구하기
    정사각형의 각 꼭지점과 중심점을 기준으로 지점이 어느 위치에 있는지 반환
    1-----------0
    | \   0   / |
    |   \   /   |
    | 1   X   3 |
    |   /   \   |
    | /   2   \ |
    2-----------3                   
    각 지점에 해당하는 숫자 반환
    '''
    if (point[0] - gcs_lng) == 0:
        if (point[1] - gcs_lat) > 0:
            return  1.571
        else:
            return  4.712

    angle = math.atan2((point[1] - gcs_lat), (point[0] - gcs_lng))

    if angle < 0:
        angle += 2*math.pi

    return angle

for i in generate_circle_points((gcs_lng, gcs_lat), 0.001):
    print(get_degree(i))