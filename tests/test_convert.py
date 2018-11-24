import os

import pytest

from foto.commands.convert import get_config_key


FIXTURES_DIR = os.path.join(os.path.dirname(__file__),
                            'fixtures_video_formats')


cases = [
    ('MOV001.3gp', '3gp'),
    ('P1010001.mkv', 'mkv'),
    ('P1160887.MOV', 'mov-panasonic-dmc-fz8'),
    ('IMG_0050.MOV', 'mov-apple-iphone-se'),
    ('trim.649C0C97-4148-45C6-BA3E-5ED42DD055C0.MOV', 'mov-apple-iphone-se'),
    ('2014-07-20 03.35.28.mp4', 'mp4-motorola-xt1069'),
    ('P1030378.MP4', 'mp4-panasonic-dmc-tz80'),
    ('051119_120308.avi', 'avi'),
]
fixtures_exist = all([
    os.path.isfile(os.path.join(FIXTURES_DIR, basename))
    for basename, expected in cases
])


@pytest.mark.skipif(not fixtures_exist,
                    reason='video fixtures are missing')
@pytest.mark.parametrize('basename,expected', cases)
def test_get_config_key(basename, expected):
    filename = os.path.join(FIXTURES_DIR, basename)
    assert get_config_key(filename) == expected
