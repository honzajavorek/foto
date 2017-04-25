import os

import yaml


config_filename = os.path.join(os.path.dirname(__file__), 'config.yml')
with open(config_filename, encoding='utf8') as f:
    config = yaml.load(f)
config['geocoding']['key'] = os.environ.get('ELK_GEOCODING_API_KEY')
