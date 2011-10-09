# -*- coding: utf-8 -*-


import os
import subprocess
import log


class VideoConverter(object):
    """ffmpeg python wrapper."""
    
    def convert(self, file):
        mov_size = os.path.getsize(file.path) / 1024 # kB
        avi_filename = os.path.splitext(file.path)[0] + '.avi'
        
        command = ('ffmpeg', '-i', file.path, '-vcodec', 'libx264', '-crf', '25.5', '-acodec', 'libmp3lame',
                   '-ab', '64kb', '-ac', '1', '-ar', '8000', '-aspect', '4:3', '-r', '30', '-coder', '1',
                   '-flags2', '+dct8x8', '-flags', '+loop', '-deblockalpha', '0', '-deblockbeta', '0', '-cmp',
                   '+chroma', '-partitions', '+parti4x4+parti8x8+partp8x8', '-me_method', 'umh', '-subq', '9',
                   '-me_range', '16', '-g', '250', '-keyint_min', '25', '-sc_threshold', '40', '-i_qfactor', '0.714',
                   '-qblur', '0.5', '-b_strategy', '1', '-threads', '2', '-trellis', '2', '-chromaoffset', '0',
                   '-qcomp', '0.60', '-qmin', '10', '-qmax', '51', '-qdiff', '4', '-y', '-f', 'avi', avi_filename)
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderrdata = process.communicate()
        
        if process.returncode > 0:
            log.error(stderrdata)
            raise subprocess.CalledProcessError(process.returncode, 'ffmpeg')
        
        avi_size = os.path.getsize(avi_filename) / 1024 # kB
        percents = 0 if not avi_size else 100 - ((int(avi_size) * 100) / int(mov_size))
        
        return avi_size, percents, avi_filename

