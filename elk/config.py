# -*- coding: utf-8 -*-


import os
import logging as log
from ConfigParser import SafeConfigParser


class Config(SafeConfigParser):

    filename = os.path.join(os.path.dirname(__file__), 'default.cfg')

    def __init__(self, *args, **kwargs):
        SafeConfigParser.__init__(self, *args, **kwargs)  # old-style class

        log.debug('Default config values taken from: ' + self.filename)
        with open(self.filename) as f:
            self.readfp(f)

        self.filename = self.get('config', 'filename')
        log.debug('Config file: ' + self.filename)

        self.remove_option('config', 'filename')
        if self.read([self.filename]):
            log.debug('Config file successfully loaded.')

    def save(self):
        dir = os.path.dirname(self.filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self.filename, 'w') as f:
            self.write(f)

    def getfilename(self, section, option):
        return os.path.expanduser(self.get(section, option))
