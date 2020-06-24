import click
from flask.cli import with_appcontext

from cuor.harvester.grid import load_grid


@click.group()
def harvester():
    """Command related to migrating/init iroko data."""


@harvester.command()
@with_appcontext
def loadgrid():
    """Init vocabularies."""
    load_grid()
