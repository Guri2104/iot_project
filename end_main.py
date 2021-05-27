from accessnet import Finder
from configurations import Config
from connectClient import Connection
from utils import *
import time


def handshake(s_socket: Connection, uid: int):

    size = get_file_size("config_v1.yaml")

    # first message contains 2 bytes of uid and 3 bytes of config file size
    first_msg = uid.to_bytes(2, byteorder="big") + size.to_bytes(3, byteorder="big")
    s_socket.s_send(first_msg)

    # first received message contains 2 bytes of new_id and 1 byte of config_required flag
    first_recv = s_socket.s_recv(3)

    # new_id is id returned by edge. If you send a non-zero
    # uid, then new_id could be equal to the uid itself
    # else if you sent a zero or a uid that's not recognized by edge
    # then you get a different new_id
    new_id = first_recv[:2]
    new_id = int.from_bytes(new_id, "big")

    config_required = int.from_bytes(bytes(first_recv[2:]), "big")

    # if config file needs to be sent to the edge
    if config_required == 1:
        f = open("config_v1.yaml", "rb")
        data = f.read(size)
        s_socket.s_send(data)
        f.close()

    return new_id


def sleep_and_reconnect(rate: int, s_socket: Connection, addr, port):
    s_socket.close()
    time.sleep(rate)
    s_socket = Connection()
    s_socket.connect_to_host(addr, int(port))


if __name__ == '__main__':
    configs = Config("config_v1.yaml")

    medium = configs.get_config_value("communication_medium")

    if medium == "wifi":
        ssid = configs.get_config_value("access_point_ssid")
        p_key = configs.get_config_value("access_point_password")
        wap = Finder(server_name=ssid, password=p_key, interface="en0")
        wap.connection()

    edge_addr = configs.get_config_value("edge_device_address")
    edge_port = configs.get_config_value("edge_device_port")
    socket = Connection()
    socket.connect_to_host(edge_addr, int(edge_port))

    # seconds between each message sent after handshake
    msg_rate = int(configs.get_config_value("transmission_rate"))

    # initially local_device_id is 0
    local_device_id = 0

    # you get a new id for future connections
    local_device_id = handshake(socket, local_device_id)

    while True:
        socket.s_send(b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01')
        if bool(configs.get_config_value("keep_alive")):
            time.sleep(msg_rate)
        else:
            sleep_and_reconnect(msg_rate, socket, edge_addr, edge_port)
            local_device_id = handshake(socket, local_device_id)

    # 0, size_of_config_file -> edge
    # 4, 1 <- edge
    # config -> edge
    #
    # start sending readings
    #
    # disconnect
    #
    # 4, size_of_config_file -> edge

    # 4, 0 <- edge # if everything is fine
    # when edge device needs to reboot, it saves the current id_config_mapping in a file
    # 4, 1 <- edge # if it requires config again

    # start sending reading


# garbage collector thread that runs every 1 hour

# it goes through each end-device configuration, delta the current time and last received time
# and compare the delta with transmission rate
# if delta  > transmission rate x 2, put it back in unused_id_heap

# edge updates end_device config structure exactly when message is received
# multithreading that will use locks to write
# select that has wait time
