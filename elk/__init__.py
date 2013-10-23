

__version__ = '3.0.0'


import os
from ConfigParser import SafeConfigParser as Config


config = Config()
config.read(os.path.join(os.path.dirname(__file__), 'default.cfg'))
