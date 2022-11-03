import click

from adapters import console
from commands.bootstrap import CommandBootstrap
from commands.check import CommandCheck
from commands.destroy import CommandDestroy


@click.group(help="CLI tool to manage buvis clusters")
def cli():
    pass


@cli.command("check")
def check():
    cmd = CommandCheck()
    cmd.execute()


@cli.command("bootstrap")
def bootstrap():
    _check_configuration()
    cmd = CommandBootstrap()
    cmd.execute()


@cli.command("destroy")
def destroy():
    _check_configuration()
    cmd = CommandDestroy()
    cmd.execute()


def _check_configuration():
    with console.capture():
        cmd = CommandCheck()
        cmd.execute()

    if cmd.check_failed:
        console.panic("There are configuration issues. Run `buvisctl check`")
    else:
        console.success("Configuration is valid")


if __name__ == "__main__":
    cli()
