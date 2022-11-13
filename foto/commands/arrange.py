import os

from foto import config
from foto.utils import list_files, creation_datetime, location


__all__ = ['arrange']


def arrange(directory):
    dir_mode = os.stat(directory).st_mode
    exts = config['media_exts']

    for filename in list_files(directory, exts=exts, recursive=True):
        basename = os.path.basename(filename)

        # create new directory with date and location hint
        date = creation_datetime(filename).date()
        new_dir_basename = '{0:%Y-%m-%d}'.format(date)

        # FIXME turn off geocoding by default
        # loc = location(filename, **config['geocoding'])
        # if loc and loc.city:
        #     new_dir_basename += ' {}, {}'.format(loc.city, loc.country)

        new_dir_filename = os.path.join(directory, new_dir_basename)
        try:
            os.makedirs(new_dir_filename, dir_mode)
        except OSError as e:
            if e.errno != 17:  # file already exists
                raise

        # FIXME turn off creating .arrange file by default
        # # create arrange file with index of moved files
        # index_basename = config['index_basename']
        # index_filename = os.path.join(new_dir_filename, index_basename)
        # with open(index_filename, 'a') as f:
        #     f.write('{0}\n'.format(filename))

        # move
        new_filename = os.path.join(new_dir_filename, basename)
        filenames = [str(f).replace(str(directory), '').lstrip('/')
                     for f in [filename, new_filename]]
        if os.path.exists(new_filename):
            print('EXISTS! {0} → {1}'.format(*filenames))
            return
        else:
            print('{0} → {1}'.format(*filenames))
            os.rename(filename, new_filename)
