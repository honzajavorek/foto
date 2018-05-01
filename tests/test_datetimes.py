import os
import shutil
import tempfile
from glob import glob
from datetime import datetime, timezone, timedelta

import pytest

from foto.commands.names import names_sort
from foto.commands.times import shift
from foto.utils import creation_datetime, format_datetime


@pytest.fixture
def fixtures_dir():
    src_path = os.path.join(os.path.dirname(__file__), 'fixtures_datetimes')
    with tempfile.TemporaryDirectory() as tmp_dir:
        for filename in glob(os.path.join(src_path, '*.jpg')):
            shutil.copy2(filename, tmp_dir)
        yield tmp_dir


@pytest.mark.parametrize('basename,expected_dt', [
    ('IMG_3087.jpg', datetime(2017, 7, 7, 15, 55, 46)),
    ('IMG_5012.jpg', datetime(2018, 5, 1, 12, 58, 47,
                              tzinfo=timezone(timedelta(hours=2)))),
    ('P1000805.jpg', datetime(2017, 7, 7, 17, 8, 0)),
])
def test_datetimes_reading(fixtures_dir, basename, expected_dt):
    dt = creation_datetime(os.path.join(fixtures_dir, basename))
    assert dt, expected_dt


@pytest.mark.parametrize('dt,expected', [
    (
        datetime(2017, 7, 7, 15, 55, 46),
        '2017:07:07 15:55:46',
    ),
    (
        datetime(2018, 5, 1, 12, 58, 47, tzinfo=timezone(timedelta(hours=2))),
        '2018:05:01 12:58:47+02:00',
    ),
    (
        datetime(2017, 7, 7, 17, 8, 0, 989),
        '2017:07:07 17:08:00.989',
    ),
])
def test_datetimes_formatting(dt, expected):
    assert format_datetime(dt) == expected


def test_sort(fixtures_dir):
    names_sort(fixtures_dir)
    assert set(os.listdir(fixtures_dir)) == set([
        '0-IMG_3087.jpg',  # 2017:07:07 15:55:46
        '1-P1000805.jpg',  # 2017:07:07 17:08:00
        '2-IMG_5012.jpg',  # 2018:05:01 12:58:47
    ])


def test_fix(fixtures_dir):
    assert (
        creation_datetime(os.path.join(fixtures_dir, 'P1000805.jpg'))
        == datetime(2017, 7, 7, 17, 8, 0, 989000)
    )

    filenames = [
        os.path.join(fixtures_dir, basename)
        for basename in os.listdir(fixtures_dir)
    ]
    list(shift(filenames, -2))

    assert (
        creation_datetime(os.path.join(fixtures_dir, 'P1000805.jpg'))
        == datetime(2017, 7, 7, 15, 8, 0, 989000)
    )
