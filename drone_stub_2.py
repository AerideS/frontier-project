from mongodb_api import DroneData

import time
device_data = DroneData()

base_longitude = 128.1
base_latitude = 35.1331
step = -0.001
for i in range(0, 100):
    time.sleep(0.5)
    print("Count : " + str(i))
    device_data.update_device_data('drone2', base_longitude + step*i,
                                    base_latitude + step * i, 30)
