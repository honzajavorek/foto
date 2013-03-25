

__version__ = '3.0.0.dev'


from gevent import monkey
monkey.patch_all()

from elk.configuration import Config
config = Config()
