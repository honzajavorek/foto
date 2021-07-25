from pathlib import Path

import click

from foto.logger import Logger
from foto.utils import list_dirs, FileFormatError


logger = Logger('foto')


@click.group()
@click.pass_context
@click.version_option()
@click.help_option()
@click.option('-d', '--dir', 'base_dir',  # NOQA
    default=Path.cwd(),
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help='Uses given directory instead of current directory',
    metavar='DIR',
)
@click.option('--batch',  # NOQA
    is_flag=True,
    help='Perform given command for each subdirectory',
)
def cli(context, base_dir, batch):
    context.obj = {'base_dir': base_dir, 'batch': batch}


def make_command(name, import_path, help):
    @cli.command(name, help=help)
    @click.pass_obj
    def command(obj, *args):
        batch = obj['batch']
        base_dir = obj['base_dir']

        directories = list_dirs(base_dir) if batch else [Path(base_dir)]
        implementation = import_command(import_path)

        try:
            for directory in directories:
                message = "🚀  Running command 'foto {}' for directory '{}'"
                logger.log(message.format(name, directory))
                implementation(directory, *args)

        except KeyboardInterrupt:
            click.echo('\n🚧  Interrupted!', err=True)
        except FileFormatError as e:
            logger.err('{} is unreadable'.format(e.filename))


def import_command(full_name):
    components = full_name.split('.')
    mod_name = '.'.join(components[0:-1])
    func_name = components[-1]
    module = __import__(mod_name, fromlist=[func_name])
    return getattr(module, func_name)


commands = [
    {
        'name': 'arrange',
        'import_path': 'foto.commands.arrange.arrange',
        'help': ('Take all mess in directory and place it into subdirectories '
                 'according to metadata'),
    },
    {
        'name': 'auto',
        'import_path': 'foto.commands.auto.auto',
        'help': 'Does all standard operations in directory',
    },
    {
        'name': 'clean',
        'import_path': 'foto.commands.clean.clean',
        'help': 'Removes rubbish',
    },
    {
        'name': 'convert',
        'import_path': 'foto.commands.convert.convert',
        'help': 'Converts all photos and videos in directory',
    },
    {
        'name': 'convert:images',
        'import_path': 'foto.commands.convert.convert_images',
        'help': 'Optimizes all images in directory',
    },
    {
        'name': 'convert:video',
        'import_path': 'foto.commands.convert.convert_video',
        'help': 'Converts and optimizes all videos in directory',
    },
    {
        'name': 'convert:audio',
        'import_path': 'foto.commands.convert.convert_audio',
        'help': 'Converts and optimizes all sounds to MP3s in directory',
    },
    {
        'name': 'captions',
        'import_path': 'foto.commands.captions.captions',
        'help': 'Print all captions in directory',
    },
    {
        'name': 'captions:fix',
        'import_path': 'foto.commands.captions.captions_fix',
        'help': 'Fix all captions in directory',
    },
    {
        'name': 'captions:clean',
        'import_path': 'foto.commands.captions.captions_clean',
        'help': 'Remove all captions in directory',
    },
    {
        'name': 'names:fix',
        'import_path': 'foto.commands.names.names_fix',
        'help': 'Fix all filenames in directory',
    },
    {
        'name': 'names:sort',
        'import_path': 'foto.commands.names.names_sort',
        'help': 'Rename all files in directory to sort them by date & time',
    },
    {
        'name': 'names:unsort',
        'import_path': 'foto.commands.names.names_unsort',
        'help': 'Remove numbered prefixes made by names:sort',
    },
    {
        'name': 'times:fix',
        'import_path': 'foto.commands.times.times_fix',
        'help': 'Fix recorded times in the directory',
    },
    {
        'name': 'info:restore',
        'import_path': 'foto.commands.info.info_restore',
        'help': ('Reads Picasa.ini, feed.rss, etc. to restore album info'
                 ' & captions, writes info.yml and metadata instead')
    },
    {
        'name': 'share:zip',
        'import_path': 'foto.commands.share.zip',
        'help': ('Create a sharing-friendly zip file with contents'
                 ' of given directory'),
    },
    {
        'name': 'share:icloud',
        'import_path': 'foto.commands.share.icloud',
        'help': ('Create a sharing-friendly zip file with contents'
                 ' of given directory and put it to the iCloud directory'),
    },
    {
        'name': 'share:photos',
        'import_path': 'foto.commands.share.photos',
        'help': ('Prepare contents of given directory for importing to'
                 ' the Apple Photos app'),
    }
]


for definition in commands:
    make_command(
        definition['name'],
        definition['import_path'],
        definition['help'],
    )


if __name__ == '__main__':
    cli()
