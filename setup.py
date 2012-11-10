# -*- coding: utf-8 -*-


import re
import os
import sys
import platform
import subprocess
from setuptools import setup, find_packages


# Hack to prevent stupid "TypeError: 'NoneType' object is not callable"
# error in multiprocessing/util.py _exit_function when running `python
# setup.py test`
try:
    import multiprocessing
except ImportError:
    pass


base_path = os.path.dirname(__file__)


def read_requirements(filename):
    """Reads requirements file and returns it's contents."""
    with open(os.path.join(base_path, filename)) as f:
        return [r.strip() for r in f.readlines() if r]


def requrement_satisfied(ubuntu_package):
    """Checks by dpkg if given Ubuntu requirement is present in system."""
    pipe = subprocess.PIPE
    process = subprocess.Popen(['dpkg-query', '--show', ubuntu_package],
                               stdout=pipe, stderr=pipe)
    search_results = process.stdout.read()
    return search_results.strip().startswith(ubuntu_package)


def print_error(message):
    """Prints error message to standard error output."""
    print >> sys.stderr, message


# examine system if all Ubuntu requirements are present
if platform.linux_distribution()[0].lower() == 'ubuntu':
    try:
        missing = [r for r in read_requirements('ubuntu_packages.txt')
                   if not requrement_satisfied(r)]
        if missing:
            msg = ('warning: following Ubuntu packages are required to '
                   'install elk, but they are not present in your '
                   'system: ' + ', '.join(missing))
            print_error(msg)

    except (OSError, subprocess.CalledProcessError):
        msg = ('warning: could not call dpkg-query to properly check '
               'requirements')
        print_error(msg)
else:
    msg = ('warning: only Ubuntu box is oficially supported, see '
           'ubuntu_packages.txt file to review requirements.')
    print_error(msg)


# standard Python requirements
install_requires = read_requirements('requirements.txt')
tests_require = ['nose==1.2.1']


# determine version
version_file = 'elk/__init__.py'
with open(os.path.join(base_path, version_file), 'r') as f:
    match = re.search(r'__version__ = \'([^\'"]*)\'', f.read())
    if match:
        version = match.group(1)
    else:
        raise RuntimeError('Missing version number.')


setup(
    name='elk',
    description='Command line photo manager',
    long_description=__doc__,
    version=version,
    author='Honza Javorek',
    author_email='jan.javorek@gmail.com',
    url='https://github.com/honzajavorek/elk',
    license='ISC',
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'elk = elk.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False
)
