# -*- coding: utf-8 -*-

"""This module contains the flask application to visualize the db."""

from .manager import Manager

if __name__ == '__main__':
    manager = Manager()
    app = manager.get_flask_admin_app()
    app.run(debug=True, host='0.0.0.0', port=5000)  # noqa
