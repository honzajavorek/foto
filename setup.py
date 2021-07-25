import sys
from setuptools import setup, find_packages


try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    message = "Unable to locate 'semantic_release', releasing won't work"
    print(message, file=sys.stderr)


version = '1.2.0'


install_requires = [
    'plumbum',
    'send2trash',
    'pync',
    'click',
    'geocoder',
    'pyaml',
    'lxml',
    'colorama',
    'python-slugify',
    'osxphotos',
]
tests_require = [
    'pytest-runner',
    'pytest',
    'coveralls',
    'pytest-cov',
    'pylama',
]
release_requires = [
    'python-semantic-release',
]


setup(
    name='foto',
    description='Command line photo manager',
    long_description=open('README.rst').read(),
    version=version,
    author='Honza Javorek',
    author_email='mail@honzajavorek.cz',
    url='https://github.com/honzajavorek/foto',
    license=open('LICENSE').read(),
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        'release': release_requires,
    },
    entry_points={
        'console_scripts': [
            'foto = foto.cli:cli',
        ],
    },
)
