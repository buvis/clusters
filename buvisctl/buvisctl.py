import os

import click

from commands.bootstrap import CommandBootstrap
from commands.destroy import CommandDestroy


@click.group(help="CLI tool to manage buvis clusters")
def cli():
    if not os.path.basename(os.getcwd()).startswith("cluster-"):
        exit("\nYou are not in cluster directory (cluster-<name>)!\n")


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
