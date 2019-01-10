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

        self.config.update(copy(data))

        with open(self.file, 'w') as cfg:
            self.config.write(cfg)

    def get(self):
        data = {}
        for section in self.config.sections():
            data[section] = dict(self.config[section].items())
        return copy(data)

    def get_section(self, section):
        if section in self.config.sections():
            return dict(self.config[section].items())
        return {}

    def get_video_src(self):
        gui_group = self.get_section('GUI')
        src = gui_group.get('video_src', '0')
        return int(src)

    def get_commands(self):
        return self.get_section('COMMANDS')

    def get_combobox(self):
        return self.get_section('COMBOBOX')

    def get_combobox_texts(self):
        return self.get_section('COMBOBOX_TEXT')

    def get_gui(self):
        return  self.get_section('GUI')
