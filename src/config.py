#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Storage.
"""


import ConfigParser as parser
import sys

class Config:

    CONFIG_FILE = "../data/app.cfg"

    __instance = None

    def __init__(self):
        """Sort of config singleton."""
        
        if Config.__instance is None:
            try:
                Config.__instance = parser.RawConfigParser()
                Config.__instance.read(self.CONFIG_FILE)
            except Exception as e:
                import log
                log.log('error', '[Configuration] %s' % e)
                sys.exit(1)
        
        # Store instance reference as the only member in the handle
        self.__dict__['_Config__instance'] = Config.__instance
        
    def __getattr__(self, attr):
        """ Delegate access to implementation """
        
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        
        return setattr(self.__instance, attr, value)
    

if __name__ == '__main__':
    pass
    
