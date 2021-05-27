from connectHost import Connection
from configurations import Config
import json


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


def get_device_readings_struct_from_list(sensor_reading_list):
    reading_dict = {}

    for reading in sensor_reading_list:
        reading_key = (list(reading.keys()))[0]
        size = reading[reading_key]
        reading_dict[reading_key] = size

    return reading_dict


def get_device_readings_as_list(configs):
    sensor_list = configs["sensors"]
    reading_list = []

    for sensor in sensor_list:
        sensor_reading_list = sensor["values"]
        for reading in sensor_reading_list:
            reading_key = (list(reading.keys()))[0]
            size = reading[reading_key]
            obj = {reading_key: size}
            reading_list.append(obj)

    return reading_list


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


def get_and_parse_init_message(c_socket: Connection):
    first_recv = c_socket.s_recv(5)

    c_id = first_recv[:2]
    c_id = int.from_bytes(c_id, "big")

    file_size = first_recv[2:5]
    file_size = int.from_bytes(file_size, "big")

    return c_id, file_size


def ask_for_config(c_socket: Connection, n_id: int, f_size: int):
    msg_ask_config = n_id.to_bytes(2, byteorder="big") + int(1).to_bytes(1, byteorder="big")
    c_socket.s_send(msg_ask_config)
    config_file = c_socket.s_recv(f_size)
    return config_file


def get_config_skeleton(config: Config):
    parsed_configs = config.get_configs()
    config_skeleton = {
        "deviceId": parsed_configs["device_id"],
        "transmission_rate": parsed_configs["transmission_rate"],
        "readings": get_device_readings_as_list(parsed_configs)
    }

    return config_skeleton


def create_final_message(data, size_list, msg_struct, keys):
    sizes_list_index = 0
    i = 0
    while i < len(data):
        value = data[i: i + size_list[sizes_list_index]]
        value = int.from_bytes(value, byteorder="big")
        msg_struct[keys[sizes_list_index]] = float(value)

        i = i + size_list[sizes_list_index]
        sizes_list_index = sizes_list_index + 1

    final_msg = json.dumps(msg_struct)

    return final_msg
