# -*- coding: utf-8 -*-


from elk.names import names_fix
from elk.optimize import optimize
from elk.captions import captions_fix


def auto(directory):
    print "Fixing filenames..."
    names_fix(directory)
    print "Fixing captions..."
    captions_fix(directory)
    optimize(directory)
