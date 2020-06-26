import click
from flask.cli import with_appcontext

from cuor.harvester.grid import load_grid
from cuor.harvester.onei import get_top_organizations, get_lower_organizations


@click.group()
def harvester():
    """Command related to migrating/init iroko data."""


@harvester.command()
@with_appcontext
def loadgrid():
    """Init vocabularies."""
    load_grid()


@harvester.command()
@with_appcontext
def gettoporg():
    """Init vocabularies."""
    get_top_organizations()


@harvester.command()
@with_appcontext
def getlowerorg():
    """Init vocabularies."""
    get_lower_organizations()
