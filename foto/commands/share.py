import re
import zipfile
import shutil
import functools
from pathlib import Path
from subprocess import run
import tempfile
from datetime import timedelta

import osxphotos
import click
from slugify import slugify

from foto import config
from foto.utils import creation_datetime, is_corrupted_file
from foto.logger import Logger


__all__ = ['zip']


ICLOUD_DIR = Path('~') / 'Library' / 'Mobile Documents' / 'com~apple~CloudDocs'

AP_HIDE_FILENAME = '.applephotoshide'
AP_MAX_BYTES = 500_000_000  # 500 MB


def zip(dir):
    logger = Logger('zip')

    zip_file = Path.cwd() / normalize(dir.with_suffix('.zip').name)
    if zip_file.exists():
        logger.err(f'Exists! {zip_file}')
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        for file_in in dir.rglob('*.*'):
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


def photos(dir):
    logger = Logger('photos')
    exts = config['photo_exts'] + config['video_exts']

    files_all = set()
    files_hidden = set()
    for file_in in Path(dir).rglob('*.*'):
        ext = file_in.suffix.lstrip('.').lower()
        if ext not in exts:
            continue
        if ext in config['video_exts'] and file_in.stat().st_size > AP_MAX_BYTES:
            logger.warn(f"Skipping {file_in.relative_to(dir)}, it's huge")
            continue
        if file_in.parent.name.endswith('_files'):
            logger.warn(f"Skipping {file_in.relative_to(dir)}, looks like a file accompanying HTML of a saved web page")
            continue
        if any([(parent / AP_HIDE_FILENAME).exists() for parent in file_in.parents]):
            files_hidden.add(file_in)
        files_all.add(file_in)
    logger.log(f'Found {len(files_all)} files')
    logger.log(f'Processing {len(files_hidden)} of those files as hidden')

    logger.log('Figuring out the oldest file in the set')
    from_date = creation_datetime(sorted(files_all)[0]) - timedelta(days=30)
    logger.log(f'Oldest file in the set: {from_date.isoformat()}')

    logger.log('Reading Apple Photos')
    photos_db = osxphotos.PhotosDB()
    existing_files = set(filter(None, (
        parse_original_filename(photo_info.original_filename) for photo_info
        in photos_db.photos(from_date=from_date)
    )))
    files_new = {f for f in files_all if f not in existing_files and f not in files_hidden}
    files_new_hidden = {f for f in files_hidden if f not in existing_files}
    logger.log(f'Found {len(files_all)} new files')
    logger.log(f'Processing {len(files_new_hidden)} of those new files as hidden')

    logger.log(f'Copying new files')
    photos_dir = Path.cwd() / f"apple-photos-import_{str(dir).replace('/', '!').strip('!')}"
    shutil.rmtree(photos_dir, ignore_errors=True)
    photos_dir.mkdir()
    for file_in in files_new:
        if is_corrupted_file(file_in):
            logger.warn(f"Skipping {file_in.relative_to(dir)}, it's corrupted")
            continue
        file_out = photos_dir / f"{str(file_in).replace('/', '!').strip('!')}"
        logger.log(f"{file_in.relative_to(dir)} → {file_out.relative_to(Path.cwd())}")
        shutil.copy2(file_in, file_out)

    logger.log(f'Copying new hidden files')
    if not files_new_hidden:
        return
    photos_dir = Path.cwd() / f"apple-photos-import-hidden_{str(dir).replace('/', '!').strip('!')}"
    shutil.rmtree(photos_dir, ignore_errors=True)
    photos_dir.mkdir()
    for file_in in files_new_hidden:
        if is_corrupted_file(file_in):
            logger.warn(f"Skipping {file_in.relative_to(dir)}, it's corrupted")
            continue
        file_out = photos_dir / f"{str(file_in).replace('/', '!').strip('!')}"
        logger.log(f"{file_in.relative_to(dir)} → {file_out.relative_to(Path.cwd())}")
        shutil.copy2(file_in, file_out)


def parse_original_filename(original_filename):
    if original_filename.startswith('Volumes!STASH'):
        return Path('/' + original_filename.replace('!', '/'))
    return None


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
