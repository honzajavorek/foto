# -*- coding: utf-8 -*-


import os
import subprocess
import tempfile
import log


class ImageMagick(object):
    """ImageMagick python wrapper."""
    
    def resize(self, file, scale):
        file_desc, file_name = tempfile.mkstemp()
        
        command = ('convert', file.path, '-resize', '%s>' % scale, file_name)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderrdata = process.communicate()
        
        if process.returncode > 0:
            log.error(stderrdata)
            raise subprocess.CalledProcessError(process.returncode, 'convert')
        
        return os.fdopen(file_desc, 'r+b'), file_name

