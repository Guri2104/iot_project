from accessnet import Finder
from configurations import Config
from connectClient import Connection
from utils_end import *
import time


if __name__ == '__main__':
    # setup configurations
    configs = Config("config_v1.yaml")
    medium = configs.get_config_value("communication_medium")

    # connect to wifi if necessary
    if medium == "wifi":
        ssid = configs.get_config_value("access_point_ssid")
        p_key = configs.get_config_value("access_point_password")
        wap = Finder(server_name=ssid, password=p_key, interface="wlan0")
        wap.connection()

    # setup socket connection. default is AF_UNIX, you can set bluetooth too
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
            socket = sleep_and_reconnect(msg_rate, socket, edge_addr, edge_port)
            local_device_id = handshake(socket, local_device_id)
