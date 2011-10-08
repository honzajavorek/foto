# -*- coding: utf-8 -*-


from application.Controller import Controller
import sys
import os
from tools.Config import Config


__author__ = 'Honza Javorek'
__copyright__ = 'Copyright 2010-2011, Honza Javorek'
__credits__ = ['Martin Javorek', 'Phil Harvey']

__version__ = '1.0'
__maintainer__ = 'Honza Javorek'
__email__ = 'honza@javorek.net'
__status__ = 'Development'


if __name__ == '__main__':
    wd = os.getcwdu() # working directory
    sd = os.path.dirname(sys.argv[0]) # script directory
    
    os.chdir(sd) # change to script's directory
    Config().set('application', 'workingDirectory', wd)
    Config().set('application', 'scriptDirectory', sd)

    Config().set('application', 'version', __version__)  
    Controller(sys.argv[1:])

