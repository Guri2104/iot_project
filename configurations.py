"""
A Python class to read, parse and set end device
configurations from a yaml file

dependencies: install PyYaml
"""

import yaml


class Config:
    def __init__(self, file_addr):
        """
        A Python class to read, parse and set end device
        configurations from a yaml file

        :param file_addr: address of the configuration file
        """
        self.__file = file_addr
        self.__configs = {}
        self.parseFile(self.__file)

    def parseFile(self, file_addr):
        """
        parses the given config file, converts the YAML scalar values
        to the Python dictionary format and saves it as self.configs

        :param file_addr: address of the configuration file
        """
        self.__file = file_addr
        with open(file_addr) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to the Python dictionary format
            self.__configs = yaml.load(file, Loader=yaml.FullLoader)

    def get_file(self):
        """Get the current file address"""
        return self.__file

    def set_file(self, file_addr):
        """Update the current file address and parse configs

        :param file_addr: address of a new config file to be set
        """
        self.parseFile(file_addr)

    def get_configs(self):
        """Get the parsed configs dictionary"""
        return self.__configs

    def get_config_keys(self):
        """Get a list of all the keys in current
        config dictionary"""
        return self.__configs.keys()

    def get_config_value(self, config_key):
        """
        Get the value of a given configuration_key
        :param config_key: Name of the configuration
        """
        return self.__configs[config_key]
