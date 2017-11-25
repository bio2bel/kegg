# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db"""

import flask_admin
from flask import Flask
from flask_admin.contrib.sqla import ModelView

from bio2bel_kegg.manager import Manager
from bio2bel_kegg.models import *


def add_admin(app, session, **kwargs):
    admin = flask_admin.Admin(app, **kwargs)
    admin.add_view(ModelView(Pathway, session))
    admin.add_view(ModelView(Protein, session))
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
