# -*- coding: utf-8 -*-

"""This module contains all the constants used in Bio2bel Kegg project."""

import os

from bio2bel import get_data_dir

MODULE_NAME = 'kegg'
DATA_DIR = get_data_dir(MODULE_NAME)

CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'config.ini')
METADATA_FILE_PATH = os.path.join(DATA_DIR, 'protein_metadata.json')  # Metadata file generated for the parser

ENTITY_DIRECTORY = os.path.join(DATA_DIR, 'entities')
os.makedirs(ENTITY_DIRECTORY, exist_ok=True)

# returns the list of human pathways
KEGG_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway'
KEGG_HUMAN_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway/hsa'

#  human genes linked from each of the KEGG pathways
PROTEIN_PATHWAY_URL = 'http://rest.kegg.jp/link/pathway'
PROTEIN_PATHWAY_HUMAN_URL = 'http://rest.kegg.jp/link/pathway/hsa'

# KEGG stats
KEGG_STATISTICS_URL = 'http://rest.kegg.jp/info/kegg'

# returns the list of organism pathways
KEGG_ORGANISM_URL = 'http://rest.kegg.jp/list/organism'

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

XREF_MAPPING = {
    'NCBI-GeneID': 'ncbigene',
    'NCBI-ProteinID': 'ncbiprotein',
    'OMIM': 'mim',
    'HGNC': 'hgnc',
    'Ensembl': 'ensembl',
    'Vega': 'vega',
    'Pharos': 'pharos',
    'UniProt': 'uniprot',
    'Pfam': 'pfam',
}
