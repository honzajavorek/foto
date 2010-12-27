#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Elk, my personal photo manager.
"""


import sys
import os
import getopt

import config


__author__ = 'Honza Javorek'
__copyright__ = 'Copyright 2010, Honza Javorek'
__credits__ = ['Martin Javorek', 'Phil Harvey']

__version__ = '0.1'
__maintainer__ = 'Honza Javorek'
__email__ = 'honza@javorek.net'
__status__ = 'Development'


class Controller:

    def __init__(self, argv):
        self.__parse_args(argv)
        
    def __run(self, action, arg=None):
        if action == 'upload':
            print 'upload'
        elif action == 'sync':
            print 'sync %s' % (arg)
        sys.exit(0)
    
    def __wrap_safe_mode(self, action, arg=None):
        if not config.Config().getboolean('application', 'debug'):
            try:
                self.__run(action, arg)
            except Exception as e:
                import log
                log.log('error', '[%s] %s' % (e.__class__.__name__, e))
                sys.exit(1)
        else:
            self.__run(action, arg)
    
    def __parse_args(self, argv):
        try:
            opts, args = getopt.getopt(argv, 'hud', ['help', 'upload', 'debug', 'sync='])
            playlist = None
            cfg = config.Config()
            
            for opt, arg in opts:
                if opt in ('-h', '--help'):
                    self.__usage()
                    sys.exit(0)
                elif opt in ('-d', '--debug'):
                    cfg.set('application', 'debug', str(True))
                elif opt in ('-u', '--upload'):
                    self.__run('upload')
                elif opt in ('--sync'):
                    self.__run('sync', arg)
                    
            self.__usage()
            sys.exit(0)
            
        except getopt.GetoptError:
            self.__usage()
            sys.exit(2)

    def __usage(self):
        print '''
Usage:
    elk [OPTIONS]
    Always works with current directory (considered then as album).

    OPTIONS:
    -h, --help        print usage summary (this screen)
    -d, --debug       debug mode
    -u, --upload      uploads current directory to Picasa
    --sync=albumID    synchronizes current directory with Picasa
'''

if __name__ == '__main__':
    wd = os.getcwdu() # working directory
    sd = os.path.dirname(sys.argv[0]) # script directory
    
    os.chdir(sd) # change to script's directory
    config.Config().set('application', 'workingDirectory', wd)
    config.Config().set('application', 'scriptDirectory', sd)
    
    Controller(sys.argv[1:])
    sys.exit(0) # exit success

