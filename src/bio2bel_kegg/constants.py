# -*- coding: utf-8 -*-

"""This module contains all the constants used in bio2bel Kegg project"""

import os

KEGG_DATA_DIR = os.path.join(os.path.expanduser('~'), '.kegg')

if not os.path.exists(KEGG_DATA_DIR):
    os.makedirs(KEGG_DATA_DIR)

KEGG_DATABASE_NAME = 'kegg.db'
KEGG_SQLITE_PATH = 'sqlite:///' + os.path.join(KEGG_DATA_DIR, KEGG_DATABASE_NAME)

KEGG_CONFIG_FILE_PATH = os.path.join(KEGG_DATA_DIR, 'config.ini')

KEGG_PATHWAYS_URL = 'http://rest.kegg.jp/list/pathway/hsa'
KEGG_GENE_MAPPING_URL = 'http://rest.kegg.jp/link/pathway/hsa'
KEGG_STATISTICS_URL = 'http://rest.kegg.jp/info/kegg'
