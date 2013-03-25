# -*- coding: utf-8 -*-


import os
import logging
from ConfigParser import SafeConfigParser


class Config(SafeConfigParser):
    """Configuration based on plaintext ``ini``-like files."""

    filename = os.path.join(os.path.dirname(__file__), 'default.cfg')

    def load(self, filename=None):
        filename = filename or self.filename
        logging.debug('Default config values taken from: %s', filename)
        with open(filename) as f:
            self.readfp(f)
        logging.debug('Config file: %s', self.filename)

    def getfilename(self, section, option):
        """Returns string as normalized filename. ``~`` wildcards
        are expanded."""
        return os.path.normpath(os.path.expanduser(self.get(section, option)))
