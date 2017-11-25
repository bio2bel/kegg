# -*- coding: utf-8 -*-

"""This module contains all the constants used in bio2bel Kegg project"""

import os

MODULE_NAME = 'kegg'
BIO2BEL_DIR = os.environ.get('BIO2BEL_DIRECTORY', os.path.join(os.path.expanduser('~'), '.pybel', 'bio2bel'))
DATA_DIR = os.path.join(BIO2BEL_DIR, MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CACHE_NAME = '{}.db'.format(MODULE_NAME)
DEFAULT_CACHE_PATH = os.path.join(DATA_DIR, DEFAULT_CACHE_NAME)
DEFAULT_CACHE_CONNECTION = os.environ.get('BIO2BEL_CONNECTION', 'sqlite:///' + DEFAULT_CACHE_PATH)

KEGG_CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')

# returns the list of human pathways
KEGG_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway/hsa'

#  human genes linked from each of the KEGG pathways
PROTEIN_PATHWAY_URL = 'http://rest.kegg.jp/link/pathway/hsa'

# KEGG stats
KEGG_STATISTICS_URL = 'http://rest.kegg.jp/info/kegg'

# Description KEGG endpoint
API_KEGG_GET = 'http://rest.kegg.jp/get/{}'
