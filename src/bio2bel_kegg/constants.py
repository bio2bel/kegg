# -*- coding: utf-8 -*-

"""This module contains all the constants used in bio2bel Kegg project"""

import os

from bio2bel.utils import get_connection, get_data_dir

MODULE_NAME = 'kegg'
KEGG = 'KEGG'
HGNC = 'HGNC'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')

# returns the list of human pathways
KEGG_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway/hsa'

#  human genes linked from each of the KEGG pathways
PROTEIN_PATHWAY_URL = 'http://rest.kegg.jp/link/pathway/hsa'

# KEGG stats
KEGG_STATISTICS_URL = 'http://rest.kegg.jp/info/kegg'

# Description KEGG endpoint
API_KEGG_GET = 'http://rest.kegg.jp/get/{}'

# Description properties
DBLINKS = 'DBLINKS'
PATHWAYS = 'PATHWAYS'

PROTEIN_RESOURCES = [
    'HGNC',
    'UniProt',
]
