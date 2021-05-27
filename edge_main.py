from configurations import Config
from connectHost import Connection
from utils_edge import *
from heap import Heap
from _thread import *
from datetime import datetime
import threading
import yaml
import time
import json

# locks required to handle concurrency
config_file_lock = threading.Lock()
heap_lock = threading.Lock()
mapping_log_lock = threading.Lock()


def handshake(client_socket: Connection):
    # get the id and config file size in the first message
    c_id, file_size = get_and_parse_init_message(client_socket)

    # if end_device sends a previously used id
    if c_id > 0:
        # check logs for record of given id's configurations
        if c_id in id_config_mapping.keys():
            client_socket.set_end_device_id(c_id)
            msg_ask_config = c_id.to_bytes(2, byteorder="big") + int(0).to_bytes(1, byteorder="big")
            client_socket.s_send(msg_ask_config)
            return

    # if c_id = 0 or c_id not found in logs then assign a new id from the heap
    heap_lock.acquire()
    new_id = int(unused_ids_heap.pop_min())
    heap_lock.release()

    # set the local_device_id for the socket connection
    client_socket.set_end_device_id(new_id)

    # send message containing new id and flag (1) asking for configuration file
    config_file_content = ask_for_config(client_socket, new_id, file_size)

    # hold configurations in a temporary file and get it's data using Config()
    config_file_lock.acquire()
    with open("config_holder.yaml", "wb") as f:
        f.write(config_file_content)
    config_obj = Config("config_holder.yaml")
    config_file_lock.release()

    # create skeleton of configurations to read incoming messages
    config_skeleton = get_config_skeleton(config_obj)

    # save skeleton to id_config_mapping dictionary as well as mapping_logs file as a backup
    id_config_mapping[new_id] = config_skeleton
    to_append = {new_id: config_skeleton}
    mapping_log_lock.acquire()
    with open('mappings_log.yaml', 'a') as yaml_file:
        yaml.safe_dump(to_append, yaml_file)
    mapping_log_lock.release()


def threaded(args):
    # create Connection object from the socket
    socket_connection = Connection(existing_socket=c_socket)

    # perform handshake
    handshake(socket_connection)

    # get end_device's local id from the Connection object
    device_id = socket_connection.end_device_id

    # get reading's list from the skeleton saved in mapping and
    # create a struct for final message to the cloud
    config_reading_list = id_config_mapping[device_id]["readings"]
    config_reading_struct = get_device_readings_struct_from_list(config_reading_list)
    reading_keys = list(config_reading_struct.keys())
    msg_to_cloud_struct = {"deviceId": id_config_mapping[device_id]["deviceId"]}
    message_size = get_device_reading_size(config_reading_struct)
    sizes = get_sizes_list(config_reading_struct)

    # receive data
    while True:
        # data received from client
        data = socket_connection.s_recv(message_size)
        # if socket is closed from the other end
        if data == b'':
            break
        data_arr = bytearray(data)

        # create timestamp of reading
        t = (datetime.now()).isoformat()
        t = t[:-3]
        t = t + 'Z'

        # save timestamp in mapping dictionary for future garbage collection
        id_config_mapping[device_id]["last_record"] = t
        # add timestamp in final message struct
        msg_to_cloud_struct["time"] = t

        final_msg = create_final_message(data_arr, sizes, msg_to_cloud_struct, reading_keys)
        print(final_msg)

        # connection closed
    socket_connection.close()


def garbage_collection():
    while True:
        time.sleep(40)
        mapping_copy = dict(id_config_mapping)
        remove_list = []
        for device in mapping_copy.keys():
            if "last_record" not in mapping_copy[device].keys():
                continue
            print(device)
            t_now = (datetime.now()).isoformat()
            t_now = t_now[:-3]
            t_now = t_now + 'Z'
            t_last_msg_recv = mapping_copy[device]["last_record"]
            t1 = datetime.strptime(t_now, "%Y-%m-%dT%H:%M:%S.%fZ")
            t2 = datetime.strptime(t_last_msg_recv, "%Y-%m-%dT%H:%M:%S.%fZ")
            delta = t1 - t2
            delta_sec = delta.seconds
            if (delta_sec/2) > (mapping_copy[device]["transmission_rate"]):
                remove_list.append(device)

        for garbage in remove_list:
            id_config_mapping.pop(garbage)

        mapping_log_lock.acquire()
        with open('mappings_log.yaml', 'w') as yaml_file:
            yaml.safe_dump(id_config_mapping, yaml_file)
        mapping_log_lock.release()


if __name__ == '__main__':
    # check for any backup logs available
    mapping_obj = Config("mappings_log.yaml")
    available_mappings = mapping_obj.get_configs()

    # main dictionary to maintain runtime mappings
    id_config_mapping = {}

    # update main dictionary with any backup mappings data
    if available_mappings is not None:
        id_config_mapping.update(available_mappings)

    # remove used id's from the unused id_heap
    used_ids = list(id_config_mapping.keys())
    unused_ids_heap = Heap(65535, used_ids)  # 2 bytes used to represent id

    # host connection
    edge_addr = "192.168.4.1"
    edge_port = 8009
    socket = Connection()
    socket.host_connection(edge_addr, int(edge_port))

    start_new_thread(garbage_collection, ())

    while True:
        c_socket, addr = socket.accept()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread for further communication
        start_new_thread(threaded, (c_socket,))
