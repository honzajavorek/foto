# -*- coding: utf-8 -*-


import os
import logging
from ConfigParser import SafeConfigParser


class Config(SafeConfigParser):
    """Configuration based on plaintext ``ini``-like files."""

    filename = os.path.join(os.path.dirname(__file__), 'default.cfg')

    def __init__(self, *args, **kwargs):
        SafeConfigParser.__init__(self, *args, **kwargs)  # old-style class

        logging.debug('Default config values taken from: %s', self.filename)
        with open(self.filename) as f:
            self.readfp(f)

        self.filename = self.get('config', 'filename')
        logging.debug('Config file: %s', self.filename)

        self.remove_option('config', 'filename')
        if self.read([self.filename]):
            logging.debug('Config file successfully loaded.')

    def save(self):
        """Saves configuration to file."""
        dir = os.path.dirname(self.filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self.filename, 'w') as f:
            self.write(f)

    def getfilename(self, section, option):
        """Returns string as normalized filename. ``~`` wildcards
        are expanded."""
        return os.path.normpath(os.path.expanduser(self.get(section, option)))
