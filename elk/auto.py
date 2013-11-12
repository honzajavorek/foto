# -*- coding: utf-8 -*-


from elk.optimize import optimize
from elk.captions import captions_fix
from elk.names import names_fix, names_sort


def auto(directory):
    print "Fixing filenames..."
    names_fix(directory)
    print "Sorting filenames..."
    names_sort(directory)
    print "Fixing captions..."
    captions_fix(directory)
    optimize(directory)
