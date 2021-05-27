import os
from connectClient import Connection
import time


def handshake(s_socket: Connection, uid: int):
    """
    perform necessary handshake with the edge device before sending the sensor readings

    :param s_socket: Connection object to handle communication with edge device
    :param uid: local_device_id of the end device, initially value is 0
    :return: new local device id for the end device
    """
    # size of config file
    st = os.stat("config_v1.yaml")
    size = st.st_size

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
    return s_socket

