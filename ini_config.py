from configparser import ConfigParser
from copy import copy
from os.path import isfile


class IniConfig(object):
    def __init__(self, file):
        self.config = ConfigParser()
        self.file = file

    def init_config(self):

        if isfile(self.file):
            with open(self.file) as cfg:
                self.config.read_file(cfg)

    def save_config(self, data):
        assert isinstance(data, dict)

        self.config['COMMANDS'] = copy(data)

        with open(self.file, 'w') as cfg:
            self.config.write(cfg)

    def get(self):
        return self.config.