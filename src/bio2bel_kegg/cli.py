# -*- coding: utf-8 -*-

from __future__ import print_function

import logging

import click

from bio2bel_kegg.manager import Manager
from bio2bel_kegg.to_belns import deploy_to_arty
from .constants import DEFAULT_CACHE_CONNECTION

log = logging.getLogger(__name__)


def set_debug(level):
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def set_debug_param(debug):
    if debug == 1:
        set_debug(20)
    elif debug == 2:
        set_debug(10)


@click.group()
def main():
    """KEGG to BEL"""
    logging.basicConfig(level=10, format="%(asctime)s - %(levelname)s - %(message)s")


@main.command()
@click.option('-v', '--debug', count=True, help="Turn on debugging.")
@click.option('-c', '--connection', help="Defaults to {}".format(DEFAULT_CACHE_CONNECTION))
@click.option('-d', '--delete_first', is_flag=True)
def populate(debug, connection, delete_first):
    """Build the local version of the full KEGG."""
    set_debug_param(debug)

    m = Manager(connection=connection)

    if delete_first or click.confirm('Drop first the database?'):
        m.drop_all()
        m.create_all()

    click.echo("populate tables")
    m.populate()


@main.command()
@click.option('-v', '--debug', count=True, help="Turn on debugging.")
@click.option('-y', '--yes', is_flag=True)
@click.option('-c', '--connection', help="Defaults to {}".format(DEFAULT_CACHE_CONNECTION))
def drop(debug, yes, connection):
    """Drop the KEGG database."""

    set_debug_param(debug)

    if yes or click.confirm('Do you really want to delete the database?'):
        m = Manager(connection=connection)
        click.echo("drop db")
        m.drop_all()


@main.command()
@click.option('--force', is_flag=True, help="Force knowledge to be uploaded even if not new namespace")
def deploy(force):
    """Deploy to Artifactory"""
    deploy_to_arty(not force)


@main.command()
@click.option('-c', '--connection', help="Defaults to {}".format(DEFAULT_CACHE_CONNECTION))
def web(connection):
    """Run web"""
    from bio2bel_kegg.web import create_app
    app = create_app(connection=connection)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
