import click
from adapters import console
from commands import (
    CommandBackup,
    CommandBackupRadicale,
    CommandBootstrap,
    CommandCheck,
    CommandDestroy,
    CommandFsck,
    CommandGenerate,
    CommandRestore,
    CommandUpdate,
)


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


@cli.command("fsck")
@click.argument("pod")
@click.option("-n",
              "--namespace",
              default="default",
              help="Namespace of the failing pod")
def fsck(pod, namespace):
    """Run fsck on Longhorn volumes of a failing pod.

    POD is the name of the pod with filesystem corruption.
    """
    cmd = CommandFsck()
    cmd.execute(pod, namespace)


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


@cli.group("backup")
def backup():
    """On-demand backups."""


@backup.command("pvc")
@click.argument("pvc")
@click.option("-n",
              "--namespace",
              default="default",
              help="Name of PVC's namespace")
def backup_pvc(pvc, namespace):
    """Backup PVC with Kopia backup cronjob.

    PVC is the name of the persistent volume claim to backup.
    """
    cmd = CommandBackup()
    cmd.execute(pvc, namespace)


@backup.command("radicale")
@click.option("-n",
              "--namespace",
              default="gtd",
              help="Namespace where Radicale runs")
@click.option("--raw",
              is_flag=True,
              help="Dump on-disk collection directories as tar.gz instead of "
                   "downloading merged ICS/VCF via Radicale's HTTP API")
def backup_radicale(namespace, raw):
    """Backup all Radicale collections to CWD.

    By default, downloads each collection as a single .ics or .vcf via
    Radicale's HTTP API (matching the web UI download). With --raw, instead
    archives each collection's on-disk directory as a timestamped .tar.gz.
    """
    cmd = CommandBackupRadicale()
    cmd.execute(namespace, raw)


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
