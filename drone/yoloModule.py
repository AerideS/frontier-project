import cv2
import torch
import pathlib
import math
import asyncio

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

BOX_SIZE_COMP_THRESHHOLD = 1.2

# 윈도우 환경에서 작동할 때 사용
# pathlib.PosixPath = pathlib.WindowsPath  # only for windows

class FindTree:
    def __init__(self):
        yolov5_path = "./yolov5"  # YOLOv5 directory
        self.image = cv2.imread(image_path)
        model_path = './best.pt'
        self.model = torch.hub.load(str(pathlib.Path(yolov5_path)), "custom", model_path, source="local", verbose=False, force_reload=True)
        self.model.eval()

        self.largest_box_area = 0
        self.largest_box_center = (0, 0)
        self.smallest_box_area = float('inf')
        self.smallest_box_center = (0, 0)
        self.closest_box_distance = float('inf')
        self.closest_box_center = (0, 0)
    
    async def process_image(self, image_obj):
        '''
        이미지를 받아 처리함
        image_ojb : cv2.imread를 통해 연 cv2.typing.MatLike
        '''
        # cv2.imshow('home', image_obj)
        self.image = image_obj
        self.half_width = int(self.image.shape[1] / 2)
        self.half_height = int(self.image.shape[0] / 2)
        
        results = self.model(image_obj)
        coord = await self.detect_objects(results)
        # if __name__ == '__main__':
        #     cv2.imshow("YOLOv5 Object Detection", self.image)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()
        return coord
    
    async def detect_objects(self, results):
        
        for result in results.pred:
            for box in result[:, :4]:
                x_center = int((box[0] + box[2]) / 2)
                y_center = int((box[1] + box[3]) / 2)
                box_width = int(box[2] - box[0])
                box_height = int(box[3] - box[1])
                box_area = box_width * box_height

                if box_area > self.largest_box_area:
                    self.largest_box_area = box_area
                    self.largest_box_center = (x_center, y_center)

                if box_area < self.smallest_box_area:
                    self.smallest_box_area = box_area
                    self.smallest_box_center = (x_center, y_center)

                distance = math.sqrt((x_center - self.half_width) ** 2 + (y_center - self.half_height) ** 2)
                if distance < self.closest_box_distance:
                    self.closest_box_distance = distance
                    self.closest_box_center = (x_center, y_center)

                cv2.circle(self.image, (x_center, y_center), 5, (0, 255, 0), -1)
                diag = math.sqrt((x_center - self.half_width) ** 2 + (y_center - self.half_height) ** 2)
                cv2.putText(self.image, f'({int(((x_center - self.half_width) / diag) * 100)}, {int(((y_center - self.half_height) / diag) * 100)}, {int(diag)}, {box_area})',
                            (x_center, y_center), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_8, False)

        if self.largest_box_area < BOX_SIZE_COMP_THRESHHOLD * self.smallest_box_area:
            closest_box_center_str = f'Closest Box Center: {self.closest_box_center}'
            print(closest_box_center_str)
            return self.closest_box_center
        else:
            largest_box_center_str = f'Largest Box Center: {self.largest_box_center}'
            print(largest_box_center_str)
            return self.largest_box_center
            
class FindTree__STUB:
    '''
    
    '''
    def __init__(self) -> None:
        '''
        초기화 과정, 
        '''
        pass
    
    async def process_image(self, image):
        '''
        작동 과정
        카메라 읽기 -> 이미지 객체 판독 -> 박스 결과 yield로 반환하기 반복
        '''
        print('find_tree_coordinate')
        return 1, 1
    
    
    
if __name__ == "__main__":
    image_path = "./tree_example3.jpg"  # �대�吏� 寃쎈줈瑜� 吏��뺥빐二쇱꽭��
    image_processor = FindTree()
    asyncio.run(image_processor.process_image(cv2.imread(image_path)))
 
 
