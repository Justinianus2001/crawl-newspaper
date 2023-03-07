#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip

import locale
from dotenv import load_dotenv

from src.elastic_search_engine import ElasticSearchEngine
from src.flask_app import FlaskApp

def setup():
    # Install packages
    # pip.main(["install", "-r", "requirements.txt"])

    # Load global variable from .env file
    load_dotenv()

    # Set locale for sorting Vietnamese characters (Windows only)
    if os.name == 'nt':
        # Windows
        locale.setlocale(locale.LC_COLLATE, 'vi_VN')

if __name__ == "__main__":
    setup()

    # Start elasticsearch server
    es = ElasticSearchEngine()
    es.run()

    # Start backend server
    app = FlaskApp(es)
    app.run()

    del app
    del es