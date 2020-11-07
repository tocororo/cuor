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
    """Load GRID data"""
    load_grid()


@harvester.command()
@with_appcontext
def gettoporg():
    """Load ONEI top organizations data."""
    get_top_organizations()


@harvester.command()
@with_appcontext
def getlowerorg():
    """Load ONEI REEUP organization data"""
    get_lower_organizations()
