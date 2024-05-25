# from api_token import *
import requests, struct, os, io

class CrawltoImage:
    def __init__(self, start_latitude, start_longitude, end_latitude, end_longitude, directory = './elevation_file/') -> None:
        self.start_latitude = start_latitude
        self.start_longitude = start_longitude
        self.end_latitude = end_latitude
        self.end_longitude = end_longitude
        self.directory = directory

    def getImagePath(self, start_latitude, start_longitude, end_latitude, end_longitude):
        return f'{self.directory}elevation_file_{start_latitude}_{start_longitude}_{end_latitude}_{end_longitude}'
    

    def fetch(self, url):
        data = b''
        response = requests.get(url)
        try_cnt = 0
        prev_lat = None
        prev_lng = None
        
        while True:
            if response.status_code == 200:  # 요청 성공
                result = response.json()
                for element in result['results']:
                    # print(result)
                    this_longitude = round(element['location']['lng'], 5)
                    this_latitude = round(element['location']['lat'], 5)

                    elev_bin = struct.pack('f', element['elevation'])
                    # print(this_latitude, this_longitude, element['elevation'], elev_bin)
                    data += elev_bin

                break

            else:  # 요청 실패
                try_cnt += 1

            if try_cnt > 3:
                data += struct.pack('f', -1.0)
                break
        return data
    

    def getHeight(self, latitude, longitude):
        url = f'https://maps.googleapis.com/maps/api/elevation/json?locations={latitude}%2C{longitude}&key={googlemap_access_token}'
        return self.fetch(url)

    def getHeightRange(self, start_latitude, start_longitude, end_latitude, end_longitude):
        samples = int(round(end_longitude*100000, 0)) - int(round(start_longitude*100000, 5)) + 1
        url =  f'https://maps.googleapis.com/maps/api/elevation/json?path={start_latitude},{start_longitude}|{end_latitude},{end_longitude}&samples={samples}&key={googlemap_access_token}'
        return self.fetch(url)


    def makeFile(self):
        this_start_latitude = self.start_latitude
        this_start_longitude = self.start_longitude
        this_end_longitude = min(round(this_start_longitude + 0.00511, 5), self.end_longitude)    
        image_path = None
        data = b''
            
        while this_end_longitude <= self.end_longitude:
            image_path = self.getImagePath(self.start_latitude, this_start_longitude, self.end_latitude, this_end_longitude)
            with open(f'{image_path}.bin', 'wb') as output:
                while this_start_latitude <= self.end_latitude:
                    print(this_start_latitude, this_start_longitude, this_start_latitude, this_end_longitude)
                    data = self.getHeightRange(this_start_latitude, this_start_longitude, this_start_latitude, this_end_longitude)
                    output.write(data)
                    this_start_latitude = round(this_start_latitude + 0.00001, 5)
                    
               
            if self.end_longitude == this_end_longitude:
                break
            data = b''
            this_start_latitude = self.start_latitude
            this_start_longitude = round(this_end_longitude + 0.00001, 5)
            this_end_longitude = min(round(this_start_longitude + 0.00511, 5), self.end_longitude)
            # print(this_start_latitude, this_start_longitude, this_start_latitude, this_end_longitude) 
            
            

class FileToAlt:
    def __init__(self, directory = '../elevation_file/') -> None:
        self.range = []
        self.directory = directory
        self.getFileList()

    def getFileList(self):
        '''
        현재 디렉토리 내의 파일 목록 추출
        고도 정보를 포함한 파일들의 목록 추출
        '''
        all_files = os.listdir(self.directory)

        # print(all_filesself.dir)

        self.alt_files = []

        for single_file in all_files:
            if self.checkFileName(single_file):
                self.alt_files.append(single_file)

        # print(self.alt_files)
        
    def checkFileName(self, file_name):
        if file_name[:15] != 'elevation_file_':
            return False
        if file_name[-4:] != '.bin':
            return False
        
        return True
    
    def getHeightFromFile(self, file_name, start_latitude, start_longitude, \
                                          end_latitude, end_longitude, latitude, longitude):
        
        offset = round(end_longitude*100000) - round(start_longitude*100000) + 1
        whole_file_dir = self.directory + file_name
        # print(offset)
        with open(whole_file_dir, 'rb') as read_file:
            try:
                # print(start_latitude, start_longitude, latitude, longitude)
                # print('size : ',(os.path.getsize(whole_file_dir)/4))
                # print('size : ',(os.path.getsize(whole_file_dir)//4))
                # print('size : ',(os.path.getsize(whole_file_dir)%4))
                height_offset = round(latitude*100000) - round(start_latitude*100000)
                width_offset = round(longitude*100000) - round(start_longitude*100000)
                total_offset =  height_offset*offset + width_offset
                # print("offset", height_offset, width_offset)
                # print("point",  latitude, ',' ,longitude)
                # print(total_offset*4)
                read_file.seek(total_offset*4)      
                raw_data = read_file.read(4)
                # print(raw_data)
                data = struct.unpack('f', raw_data)
                # print(data)
                # print("-----------------------------")
                return data[0]

            except io.UnsupportedOperation:
                pass


    def getHeight(self, latitude, longitude):
        #print(latitude, longitude)
        for single_file in self.alt_files:
            first = single_file.find('_')
            secnd = single_file.find('_', first+1)
            third = single_file.find('_', secnd+1)
            forth = single_file.find('_', third+1)
            fifth = single_file.find('_', forth+1)

            start_latitude = float(single_file[secnd+1:third])
            start_longitude = float(single_file[third+1:forth])
            end_latitude = float(single_file[forth+1:fifth])
            end_longitude = float(single_file[fifth+1:-4])

            # print(start_latitude, start_longitude, end_latitude, end_longitude, sep="  ")

            if (start_latitude <= latitude <= end_latitude) and (start_longitude <= longitude <= end_longitude):
                # print(single_file)
                ans = self.getHeightFromFile(single_file, start_latitude, start_longitude, \
                                          end_latitude, end_longitude, latitude, longitude)
                if ans != None:
                    return ans
                
    def getAllLatitude(self, latitude, start_longitude, end_longitude):
        altitude = []
        longitude = []

        while start_longitude <= end_longitude:
            this_altitude = self.getHeight(latitude, start_longitude)
            altitude.append(this_altitude)
            longitude.append(start_longitude)

            start_longitude = round(start_longitude + 0.00001, 5)

        return altitude, longitude
        

    def getAllLongitude(self, longitude, start_latitude, end_latitude):
        altitude = []
        latitudes = []

        while start_latitude <= end_latitude:
            this_altitude = self.getHeight(start_latitude, longitude)
            altitude.append(this_altitude)
            latitudes.append(start_latitude)

            start_latitude = round(start_latitude + 0.00001, 5)

        return altitude, latitudes
        
if __name__ == '__main__':
    # converter = CrawltoImage(35.14864, 128.06176, 35.14874, 128.06186)
    # converter = CrawltoImage(35.14864, 128.08224, 35.16801, 128.08735)
    # converter = CrawltoImage(35.14864, 128.08224, 35.16801, 128.08735)
    # converter = CrawltoImage(35.14864, 128.08224, 35.14864, 128.08225)
    converter = CrawltoImage(35.14864, 128.08736, 35.16801, 128.09247)
    # converter.makeFile()
    # print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
    # # print(cnt, height_cnt)
    alt_data = FileToAlt()
    # print(alt_data.getHeight(35.14864, 128.08224))
    # print(alt_data.getHeight(35.16801, 128.08735))
    print(alt_data.getHeight(35.16223, 128.08989))
    # print(alt_data.getHeight(35.14864, 128.08225))
    # print(alt_data.getHeight(35.14864, 128.08735))
    # print(alt_data.getHeight(35.14865, 128.08735))
    # print(alt_data.getHeight(35.14864, 128.08735))
    # print(alt_data.getHeight(35.14865, 128.08224))
    # print(alt_data.getHeight(35.14866, 128.08224))
    # print(alt_data.getHeight(35.14867, 128.08224))


    # print(alt_data.getHeight(35.15165, 128.08420))
    # print(alt_data.getHeight(35.15165, 128.08445))
    # print(alt_data.getHeight(35.16801, 128.08735))
