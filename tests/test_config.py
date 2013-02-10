# -*- coding: utf-8 -*-


import os
import shutil
import tempfile
from ConfigParser import NoOptionError

from elk import config
from .base import TestCase


class Config(config.Config):
    pass


class ConfigTest(TestCase):

    default_basename = 'default.cfg'
    user_basename = 'user.cfg'

    def setUp(self):
        temp_dir = tempfile.mkdtemp()
        self.temp_dir = temp_dir

        default_config = os.path.join(temp_dir, self.default_basename)
        user_config = os.path.join(temp_dir, self.user_basename)

        with open(default_config, 'w') as f:
            f.write(('[config]\nfilename = {0}\n'
                     '[smurfs]\ncap_color = white\n').format(user_config))
        self.default_config = default_config

        with open(user_config, 'w') as f:
            f.write('[smurfs]\ncap_color = red')
        self.user_config = user_config

        config_cls = Config
        config_cls.filename = default_config
        self.config_cls = config_cls

    def test_init(self):
        cfg = self.config_cls()
        self.assertEqual(cfg.filename, self.user_config)
        self.assertRaises(NoOptionError, cfg.get, 'config', 'filename')
        self.assertEqual(cfg.get('smurfs', 'cap_color'), 'red')

    def test_set_get(self):
        cfg = self.config_cls()
        size = '30'
        cfg.set('smurfs', 'size', size)
        self.assertEqual(cfg.get('smurfs', 'size'), size)

    def test_get_save(self):
        cfg = self.config_cls()
        filename = '~/gargamel.txt'
        cfg.set('smurfs', 'enemy_file', filename)
        cfg.save()

        with open(self.user_config) as f:
            contents = f.read()
        self.assertIn(filename, contents)

        cfg = self.config_cls()
        self.assertEqual(cfg.get('smurfs', 'enemy_file'),
                         filename)

    def test_get_filename(self):
        cfg = self.config_cls()
        filename = '~/gargamel.txt'
        cfg.set('smurfs', 'enemy_file', filename)
        self.assertEqual(cfg.getfilename('smurfs', 'enemy_file'),
                         os.path.expanduser(filename))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
