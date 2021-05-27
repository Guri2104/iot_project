"""
A Python class to communicate with End device over TCP using
Python sockets.
"""

import socket


class Connection:
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, protocol=0, existing_socket=None):
        """
        create a socket of given family, type and protocol.
        maintains a mapping to end-device id

        :param family: defines the addr family od the socket. Default value is socket.AF_INET.
         for bluetooth, use socket.AF_BLUETOOTH.
        :param type: defines the type of transport protocol. Default value is socket.SOCK_STREAM
        :param protocol: defines the protocol followed by the AF. Default is 0.
         for bluetooth, use socket.BTPROTO_RFCOMM.
        """
        if existing_socket is not None:
            self.host_socket = existing_socket
        else:
            self.host_socket = socket.socket(family, type, protocol)
        self.end_device_id = 0

    def host_connection(self, address, port):
        """
        binds and listens for connections on given address and port number.

        :param address: defines the IP address or a MAC address based on the
         physical medium used. E.g. If Wi-fi then IP, else if Bluetooth
         then MAC address
        :param port: define the Network port number on the host device
        """

        # Connect to the specified host and port
        self.host_socket.bind((address, int(port)))
        self.host_socket.listen()

    def set_end_device_id(self, id):
        """
        updates the record of end_device (end_device_id) connected
        through this socket

        :param id: id of end_device connected
        """
        self.end_device_id = id

    def s_recv(self, size):
        """
        Receives a packet with specified size from the server

        :param size: expected size of message
        :return: bytes
        """
        self.host_socket.setblocking(True)

        msg = self.host_socket.recv(size)
        return msg

    def s_send(self, msg):
        """Sends a message to the server with an agreed command type token
            to ensure the message is delivered safely.

        :param msg: message to be sent through socket
        """

        # try:
        self.host_socket.send(msg)

    def close(self):
        """Shut down the socket and close it"""
        # Shut down the socket to prevent further sends/receives
        try:
            # self.host_socket.shutdown(socket.SHUT_RDWR)
            # Close the socket
            self.host_socket.close()
        except OSError as err:
            raise err

    def accept(self):
        return self.host_socket.accept()

