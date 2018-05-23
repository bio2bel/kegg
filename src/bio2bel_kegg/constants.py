# -*- coding: utf-8 -*-

"""This module contains all the constants used in bio2bel Kegg project"""

import os

from bio2bel import get_data_dir

MODULE_NAME = 'kegg'
DATA_DIR = get_data_dir(MODULE_NAME)

CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')
METADATA_FILE_PATH = os.path.join(DATA_DIR, 'protein_metadata.json')  # Metadata file generated for the parser

PROTEIN_ENTRY_DIR = os.path.join(DATA_DIR, 'proteins')
os.makedirs(PROTEIN_ENTRY_DIR, exist_ok=True)

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

# Namespace constants

KEGG = 'KEGG'
HGNC = 'HGNC'
PROTEIN_RESOURCES = [
    'HGNC',
    'UniProt',
]
