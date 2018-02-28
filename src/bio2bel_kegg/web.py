# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db"""

import flask_admin
from flask import Flask
from flask_admin.contrib.sqla import ModelView

from .manager import Manager
from .models import *


class PathwayView(ModelView):
    """Pathway view in Flask-admin"""
    column_searchable_list = (
        Pathway.kegg_id,
        Pathway.name
    )


class ProteinView(ModelView):
    """Protein view in Flask-admin"""
    column_searchable_list = (
        Protein.kegg_id,
        Protein.uniprot_id,
        Protein.hgnc_id
    )


def add_admin(app, session, **kwargs):
    admin = flask_admin.Admin(app, **kwargs)
    admin.add_view(PathwayView(Pathway, session))
    admin.add_view(ProteinView(Protein, session))
    return admin


def create_app(connection=None, url=None):
    """Creates a Flask application

    :type connection: Optional[str]
    :rtype: flask.Flask
    """
    app = Flask(__name__)
    manager = Manager(connection=connection)
    add_admin(app, manager.session, url=url)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
