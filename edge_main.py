from configurations import Config
from connectHost import Connection
from utils import *
from heap import Heap
from _thread import *
from datetime import datetime
import threading
import yaml
import json


config_file_lock = threading.Lock()
heap_lock = threading.Lock()
mapping_log_lock = threading.Lock()


def handshake(client_socket: Connection):

    first_recv = client_socket.s_recv(5)

    c_id = first_recv[:2]
    c_id = int.from_bytes(c_id, "big")

    if c_id > 0:
        if c_id in id_config_mapping.keys():
            client_socket.set_end_device_id(c_id)
            msg_ask_config = c_id.to_bytes(2, byteorder="big") + int(0).to_bytes(1, byteorder="big")
            client_socket.s_send(msg_ask_config)
            return

    heap_lock.acquire()
    new_id = int(unused_ids_heap.pop_min())
    heap_lock.release()
    client_socket.set_end_device_id(new_id)
    msg_ask_config = new_id.to_bytes(2, byteorder="big") + int(1).to_bytes(1, byteorder="big")
    client_socket.s_send(msg_ask_config)

    file_size = first_recv[2:5]
    file_size = int.from_bytes(file_size, "big")

    config_file_content = client_socket.s_recv(file_size)

    config_file_lock.acquire()
    f = open("config_holder.yaml", "wb")
    f.write(config_file_content)
    f.close()
    config_obj = Config("config_holder.yaml")
    parsed_configs = config_obj.get_configs()
    config_file_lock.release()
    config_skeleton = {
        "deviceId": parsed_configs["device_id"],
        "readings": get_device_readings_struct(parsed_configs)
    }
    id_config_mapping[new_id] = config_skeleton
    to_append = { new_id : config_skeleton }
    mapping_log_lock.acquire()
    with open('mappings_log.yaml', 'a') as yamlfile:
        yaml.safe_dump(to_append, yamlfile)
    mapping_log_lock.release()


def threaded(args):
    socket_connection = Connection(existing_socket=c_socket)
    handshake(socket_connection)
    device_id = socket_connection.end_device_id
    config_reading_struct = id_config_mapping[device_id]["readings"]
    reading_keys = list(config_reading_struct.keys())
    msg_to_cloud_struct = id_config_mapping[device_id]
    message_size = get_device_reading_size(config_reading_struct)
    sizes = get_sizes_list(config_reading_struct)
    while True:
        # data received from client
        data = socket_connection.s_recv(message_size)
        if data == b'':
            break
        t = (datetime.now()).isoformat()
        t = t[:-3]
        t = t + 'Z'
        id_config_mapping[device_id]["last_record"] = t
        msg_to_cloud_struct["time"] = t
        data_arr = bytearray(data)

        sizes_list_index = 0
        i = 0
        while i < len(data_arr):
            value = data_arr[i: i + sizes[sizes_list_index]]
            value = int.from_bytes(value, byteorder="big")
            msg_to_cloud_struct["readings"][reading_keys[sizes_list_index]] = float(value)

            i = i + sizes[sizes_list_index]
            sizes_list_index = sizes_list_index + 1

        final_msg = json.dumps(msg_to_cloud_struct)
        print(final_msg)
        # connection closed
    socket_connection.close()


if __name__ == '__main__':
    mapping_obj = Config("mappings_log.yaml")
    id_config_mapping = {}
    available_mappings = mapping_obj.get_configs()
    if available_mappings is not None:
        id_config_mapping.update(available_mappings)
    used_ids = list(id_config_mapping.keys())
    unused_ids_heap = Heap(255, used_ids)

    edge_addr = "127.0.0.1"
    edge_port = 8009
    socket = Connection()
    socket.host_connection(edge_addr, int(edge_port))

    while True:
        c_socket, addr = socket.accept()

        # lock acquired by client
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c_socket,))
