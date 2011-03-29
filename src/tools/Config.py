#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser as parser



class Config:
    """Configuration storage."""



    CONFIG_FILE = "../application/config.ini"
    __instance = None



    def __init__(self):
        """Sort of config singleton."""
        
        if Config.__instance is None:
            Config.__instance = parser.RawConfigParser()
            Config.__instance.read(self.CONFIG_FILE)
        
        # Store instance reference as the only member in the handle
        self.__dict__['_Config__instance'] = Config.__instance



    def __getattr__(self, attr):
        """Delegate access to implementation."""
        
        return getattr(self.__instance, attr)



    def __setattr__(self, attr, value):
        """Delegate access to implementation."""
        
        return setattr(self.__instance, attr, value)



if __name__ == '__main__':
    pass



