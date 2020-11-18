# -*- coding: utf-8 -*-

"""This module contains all the constants used in Bio2bel Kegg project."""

import os

from bio2bel import get_data_dir

MODULE_NAME = 'kegg'
DATA_DIR = get_data_dir(MODULE_NAME)

CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')
METADATA_FILE_PATH = os.path.join(DATA_DIR, 'protein_metadata.json')  # Metadata file generated for the parser

PROTEIN_ENTRY_DIR = os.path.join(DATA_DIR, 'proteins')
os.makedirs(PROTEIN_ENTRY_DIR, exist_ok=True)

# returns the list of human pathways
KEGG_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway'
KEGG_HUMAN_PATHWAYS_URL = f'{KEGG_PATHWAYS_URL}/hsa'

# returns the list of organism pathways
KEGG_ORGANISM_URL = 'http://rest.kegg.jp/list/organism'

#  human genes linked from each of the KEGG pathways
PROTEIN_PATHWAY_URL = 'http://rest.kegg.jp/link/pathway/'
PROTEIN_PATHWAY_HUMAN_URL = f'{PROTEIN_PATHWAY_URL.rstrip("/")}/hsa'

# KEGG stats
KEGG_STATISTICS_URL = 'http://rest.kegg.jp/info/kegg'

# Description KEGG endpoint
API_KEGG_GET = 'http://rest.kegg.jp/get/{}'

# Description properties
DBLINKS = 'DBLINKS'
PATHWAYS = 'PATHWAYS'

# Namespace constants

KEGG = 'kegg'
HGNC = 'hgnc'
PROTEIN_RESOURCES = [
    'HGNC',
    'UniProt',
]
