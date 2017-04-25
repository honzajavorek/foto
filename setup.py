import sys
from setuptools import setup, find_packages


try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    message = "Unable to locate 'semantic_release', releasing won't work"
    print(message, file=sys.stderr)


version = '1.0.0'


install_requires = [
    'plumbum',
    'send2trash',
    'pync',
    'arrow',
    'click',
    'geocoder',
    'pyaml',
    'lxml',
    'colorama',
    'python-slugify',
]
tests_require = [
    'pytest-runner',
    'pytest',
    'flake8',
    'coveralls',
    'pytest-cov',
]
release_requires = [
    'python-semantic-release',
]


setup(
    name='elk',
    description='Command line photo manager',
    long_description=open('README.rst').read(),
    version=version,
    author='Honza Javorek',
    author_email='mail@honzajavorek.cz',
    url='https://github.com/honzajavorek/elk',
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
            'elk = elk.cli:cli',
        ],
    },
)
