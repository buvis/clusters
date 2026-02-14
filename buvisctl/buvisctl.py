import click

from adapters import console
from commands import (CommandBackup, CommandBootstrap, CommandCheck,
                      CommandDestroy, CommandGenerate, CommandRestore,
                      CommandUpdate)


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


@cli.command("update")
@click.argument("component")
@click.argument("version", required=False)
def update(component, version):
    """Update buvis component

    Supported components:
    - flux
    - talos
    - cilium <version>
    """
    _check_configuration()
    cmd = CommandUpdate()
    cmd.execute(component, version)


@cli.command("destroy")
def destroy():
    _check_configuration()
    cmd = CommandDestroy()
    cmd.execute()


@cli.command("restore")
@click.argument("pvc")
@click.option("-n",
              "--namespace",
              default="default",
              help="Name of PVC's namespace")
@click.option(
    "-s",
    "--snapshot",
    default="",
    help="Kopia snapshot ID. Will use latest if not specified",
)
def restore(pvc, namespace, snapshot):
    """Restore PVC from Kopia backup.

    PVC is the name of the persistent volume claim to restore.
    """
    cmd = CommandRestore()
    cmd.execute(pvc, namespace, snapshot)


@cli.command("backup")
@click.argument("pvc")
@click.option("-n",
              "--namespace",
              default="default",
              help="Name of PVC's namespace")
def backup(pvc, namespace):
    """Backup PVC with Kopia backup cronjob.

    PVC is the name of the persistent volume claim to backup.
    """
    cmd = CommandBackup()
    cmd.execute(pvc, namespace)


@cli.command("generate")
@click.argument("kind")
@click.argument("name")
@click.option("-n", "--namespace", default="default", help="Name of namespace")
def generate(kind, name, namespace):
    cmd = CommandGenerate()
    cmd.execute(kind, name, namespace)


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
