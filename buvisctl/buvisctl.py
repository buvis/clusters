import click

from commands.bootstrap import CommandBootstrap
from commands.destroy import CommandDestroy


@click.group(help="CLI tool to manage full development cycle of projects")
def cli():
    pass


@cli.command("bootstrap")
def bootstrap():
    cmd = CommandBootstrap()
    cmd.execute()


@cli.command("destroy")
def destroy():
    cmd = CommandDestroy()
    cmd.execute()


if __name__ == "__main__":
    cli()
