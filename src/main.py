#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Elk, my personal photo manager.
"""


from glob import glob
import config
import getopt
import log
import os
import sync
import sys
import upload



__author__ = 'Honza Javorek'
__copyright__ = 'Copyright 2010-2011, Honza Javorek'
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
            u = upload.Uploader()
            u.run()
        elif action == 'sync':
            s = sync.Synchronizer(arg)
            s.run()
        elif action == 'clear':
            count = 0
            for pattern in config.Config().get('settings', 'temporary').split(';'):
                log.log('info', 'Clearing all %s files.' % pattern)
                for f in glob(os.path.join(config.Config().get('application', 'workingDirectory'), pattern)):
                    os.remove(f)
                    count += 1
            log.log('ok', 'Cleared %d files.' % count)
        sys.exit(0)
    
    def __wrap_safe_mode(self, action, arg=None):
        if not config.Config().getboolean('application', 'debug'):
            try:
                self.__run(action, arg)
            except Exception as e:
                log.log('error', '[%s] %s' % (e.__class__.__name__, e))
                sys.exit(1)
        else:
            self.__run(action, arg)
    
    def __parse_args(self, argv):
        try:
            opts, args = getopt.getopt(argv, 'hudsc', ['help', 'upload', 'debug', 'sync=', 'clear', 'clean']) #@UnusedVariable
            cfg = config.Config()
            
            for opt, arg in opts:
                if opt in ('-h', '--help'):
                    self.__usage()
                    sys.exit(0)
                elif opt in ('-d', '--debug'):
                    cfg.set('application', 'debug', str(True))
                    log.log('info', 'Debug mode.')
                elif opt in ('-u', '--upload'):
                    log.log('info', 'Starting upload.')
                    self.__wrap_safe_mode('upload')
                elif opt in ('-s', '--sync'):
                    log.log('info', 'Starting synchronization.')
                    self.__wrap_safe_mode('sync', arg)
                elif opt in ('-c', '--clear', '--clean'):
                    log.log('warning', 'Clearing all temporary files!')
                    self.__wrap_safe_mode('clear', arg)
                    
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
    -h, --help              print usage summary (this screen)
    -d, --debug             debug mode
    -u, --upload            uploads current directory to Picasa
    -s, --sync=albumID      synchronizes current directory with Picasa
                            (albumID: name or hash, current dir name taken as default)
    -c, --clear             clears all temporary *_original and *_uploaded files in current directory
'''

if __name__ == '__main__':
    wd = os.getcwdu() # working directory
    sd = os.path.dirname(sys.argv[0]) # script directory
    
    os.chdir(sd) # change to script's directory
    config.Config().set('application', 'workingDirectory', wd)
    config.Config().set('application', 'scriptDirectory', sd)
    
    Controller(sys.argv[1:])
    sys.exit(0) # exit success

