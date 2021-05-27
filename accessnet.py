"""
Search for a specific WAP ssid and connect to it.
"""
import os


class Finder:
    def __init__(self, *args, **kwargs):
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        self.main_dict = {}

    def connection(self):
        try:
            result = self.connectToWAP()
        except Exception as exp:
            print("Couldn't connect to name : {}. {}".format(self.server_name, exp))
        else:
            if result:
                print("Successfully connected to {}".format(self.server_name))

    def connectToWAP(self):
        try:
            num = os.system("wpa_cli -i %s add_network" % self.interface_name)

            num1 = os.system('wpa_cli -i %s set_network 0 ssid \'"%s"\'' % (self.interface_name, self.server_name))
            if self.password is not None:
                os.system('wpa_cli -i %s set_network 0 psk \'"%s"\'' % (self.interface_name, self.password))

            os.system("wpa_cli -i %s select_network 0" % self.interface_name)
        except:
            raise Exception
        else:
            return True


if __name__ == "__main__":
    # Server_name is a case insensitive string, and/or regex pattern which demonstrates
    # the name of targeted WIFI device or a unique part of it.
    server_name = "RPiEdge"
    password = " "
    interface_name = "wlan0"
    F = Finder(server_name=server_name,
               password=password,
               interface=interface_name)
    F.connection()
