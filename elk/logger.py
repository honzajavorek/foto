import click


class Logger():

    def __init__(self, name):
        self.name = name

    def log(self, message):
        click.echo(
            click.style(self.name + ' ', dim=True) +
            message
        )

    def warn(self, message):
        click.echo(
            click.style(self.name + ' ', dim=True) +
            click.style(' {} '.format(message), bg='blue', fg='white', bold=True)
        , err=True)

    def err(self, message):
        click.echo(
            click.style(self.name + ' ', dim=True) +
            click.style(' {} '.format(message), bg='red', fg='white', bold=True)
        , err=True)
