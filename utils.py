import os


def get_cloud_id(configs):
    return configs["device_id"]


def get_device_readings_struct(configs):
    sensor_list = configs["sensors"]
    reading_dict = {}

    for sensor in sensor_list:
        sensor_reading_list = sensor["values"]
        for reading in sensor_reading_list:
            reading_key = (list(reading.keys()))[0]
            size = reading[reading_key]
            reading_dict[reading_key] = size

    return reading_dict


def get_device_reading_size(reading_struct):
    total_bytes = 0
    for size in reading_struct.values():
        if size == "byte":
            total_bytes += 1
        elif size == "short":
            total_bytes += 2
        elif size == "int" or size == "float":
            total_bytes += 4
        elif size == "long" or size == "double":
            total_bytes += 8

    return total_bytes


def get_sizes_list(reading_struct):
    sizes = []
    for size in reading_struct.values():
        if size == "byte":
            sizes.append(1)
        elif size == "short":
            sizes.append(2)
        elif size == "int" or size == "float":
            sizes.append(4)
        elif size == "long" or size == "double":
            sizes.append(8)

    return sizes


def get_file_size(file_addr):
    st = os.stat(file_addr)
    return st.st_size
