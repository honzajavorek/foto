# -*- coding: utf-8 -*-


import re
import os

from setuptools import setup, find_packages


base_path = os.path.dirname(__file__)


# read requirements
lines = open('requirements.txt').read().splitlines()
install_requires = filter(None, [line.split('#')[0].strip() for line in lines])


# determine version
code = open('elk/__init__.py', 'r').read(1000)
version = re.search(r'__version__ = \'([^\']*)\'', code).group(1)


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
    entry_points={
        'console_scripts': [
            'elk = elk.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False
)
