import click


class Logger():

    def __init__(self, name):
        self.name = name

    def log(self, message):
        click.echo(
            click.style(self.name + ' ', dim=True)
            + message
        )

    def warn(self, message):
        style = {'bg': 'blue', 'fg': 'white', 'bold': True}
        message = (
            click.style(self.name + ' ', dim=True)
            + click.style(' {} '.format(message), **style)
        )
        click.echo(message, err=True)

    def err(self, message):
        style = {'bg': 'red', 'fg': 'white', 'bold': True}
        message = (
            click.style(self.name + ' ', dim=True)
            + click.style(' {} '.format(message), **style)
        )
        click.echo(message, err=True)

    def prompt(self, message, **kwargs):
        message = (
            click.style(self.name + ' ', dim=True) + message
        )
        return click.prompt(message, **kwargs)
