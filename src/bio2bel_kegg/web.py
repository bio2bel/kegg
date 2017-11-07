# -*- coding: utf-8 -*-

""" This module contains the flask application to visualize the db"""

import flask
import flask_admin
from flask_admin.contrib.sqla import ModelView

from bio2bel_kegg.manager import Manager
from bio2bel_kegg.models import *

app = flask.Flask(__name__)
admin = flask_admin.Admin(app)

manager = Manager()

admin.add_view(ModelView(Pathway, manager.session))
admin.add_view(ModelView(Protein, manager.session))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
