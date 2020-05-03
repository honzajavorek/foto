import re
import zipfile
import shutil
import functools
from pathlib import Path
from subprocess import run
import tempfile

import click
from slugify import slugify

from foto import config
from foto.logger import Logger


__all__ = ['zip']


ICLOUD_DIR = Path('~') / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'


def zip(dir):
    logger = Logger('zip')

    zip_file = Path.cwd() / normalize(dir.with_suffix('.zip').name)
    if zip_file.exists():
        logger.err(f'Exists! {zip_file}')
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        for file_in in dir.rglob(f'*.*'):
            ext = parse_ext(file_in)
            if ext == 'heic':
                file_out_rel = file_in.relative_to(dir).with_suffix('.jpg')
                file_out_rel = normalize(file_out_rel)

                file_out = tmp_dir / file_out_rel
                file_out.parent.mkdir(parents=True, exist_ok=True)

                file_out_fmt = f'(zip)/{file_out_rel}'
                file_out_fmt = click.style(file_out_fmt, fg='green')
                logger.log(f"{file_in.relative_to(dir)} → {file_out_fmt}")

                run(['magick', 'convert', file_in, file_out], check=True)

            elif ext in config['media_exts']:
                file_in_rel = file_in.relative_to(dir)
                file_out = tmp_dir / normalize(file_in_rel)
                file_out_rel = file_out.relative_to(tmp_dir)
                file_out_fmt = click.style(f'(zip)/{file_out_rel}', fg='green')
                logger.log(f'{file_in_rel} → {file_out_fmt}')

                file_out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_in, file_out)

        size = config['share']['photo_max_size']
        for file_photo in tmp_dir.rglob('*.*'):
            if parse_ext(file_photo) not in config['photo_exts']:
                continue

            logger.log(f'(zip)/{file_photo.relative_to(tmp_dir)} → {size}px')
            run(['magick', 'convert', file_photo, '-resize',
                f'{size}x{size}>', file_photo], check=True)

        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as z:
            for filename in tmp_dir.glob('**/*.*'):
                if filename.is_dir():
                    continue

                filename_rel = filename.relative_to(tmp_dir)
                logger.log(f"{filename_rel} → zip")
                z.write(filename, filename_rel)

        logger.log(click.style(str(zip_file), bold=True))
        return zip_file


def icloud(dir):
    zip_file_in = zip(dir)
    zip_file_out = ICLOUD_DIR.expanduser() / zip_file_in.name

    logger = Logger('icloud')
    logger.log(click.style(str(zip_file_out), bold=True))
    shutil.move(zip_file_in, zip_file_out)


def normalize(path):
    path = Path(re.sub(r'\.jpeg$', '.jpg', str(path), re.I))

    parts = list(path.parts)
    suffix = path.suffix
    parts[-1] = re.sub(rf'{re.escape(suffix)}$', '', parts[-1])

    clean = functools.partial(slugify,
                              regex_pattern=r'[^\-a-z0-9_]+',
                              max_length=100)
    parts = list(map(clean, parts))
    parts[-1] = parts[-1] + suffix.lower()

    return Path(*parts)


def parse_ext(path):
    return path.suffix.lower().lstrip('.')
