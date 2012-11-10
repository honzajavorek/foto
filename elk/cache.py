# -*- coding: utf-8 -*-


import os
import json


class Cache(dict):

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super(Cache, self).__init__(*args, **kwargs)

        contents = None
        try:
            with open(filename) as f:
                contents = f.read()
        except IOError:
            pass  # not readable, no defaults then

        if contents:
            self.update(json.loads(contents))

    def save(self):
        dir = os.path.dirname(self.filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self))
