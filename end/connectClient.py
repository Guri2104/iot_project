"""
A Python class to communicate with Edge computer over TCP using
Python sockets.
"""

import socket


class Connection:
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, protocol=0):
        """
        create a socket of given family, type and protocol.

        :param family: defines the addr family od the socket. Default value is socket.AF_INET.
         for bluetooth, use socket.AF_BLUETOOTH.
        :param type: defines the type of transport protocol. Default value is socket.SOCK_STREAM
        :param protocol: defines the protocol followed by the AF. Default is 0.
         for bluetooth, use socket.BTPROTO_RFCOMM.
        """
        self.client_socket = socket.socket(family, type, protocol)

    def connect_to_host(self, address, port) -> bool:
        """
        Keeps repeating connecting to the Edge and returns True if
        connected successfully.

        :param address: defines the IP address or a MAC address based on the
         physical medium used. E.g. If Wi-fi then IP, else if Bluetooth
         then MAC address
        :param port: define the Network port number on the host device
        :return: boolean. returns True if connected successfully
        """

        while True:
            try:
                print("Connecting to the edge...")
                # Connection time out 10 seconds
                self.client_socket.settimeout(10)
                # Connect to the specified host and port
                self.client_socket.connect((address, int(port)))
                # Return True if connected successfully
                return True
            except:
                # Caught an error
                print("There is an error when trying to connect to " +
                      str(address) + "::" + str(port))

    def s_recv(self, size):
        """
        Receives a packet with specified size from the server

        :param size: expected size of message
        :return: bytes
        """
        self.client_socket.setblocking(True)

        msg = self.client_socket.recv(size)
        return msg

    def s_send(self, msg):
        """Sends a message to the server with an agreed command type token
            to ensure the message is delivered safely.

        :param msg: message to be sent through socket
        """

        # try:
        self.client_socket.send(msg)

    def close(self):
        """Shut down the socket and close it"""
        # Shut down the socket to prevent further sends/receives
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
            # Close the socket
            self.client_socket.close()
        except OSError as err:
            raise err
