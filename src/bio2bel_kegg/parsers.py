# -*- coding: utf-8 -*-

"""This module parsers the KEGG pathway names file.

The "Complete list of pathways" file maps the KEGG identifiers to their corresponding pathway name .
"""

from typing import Optional

import pandas as pd

from bio2bel.utils import ensure_path
from .constants import KEGG_PATHWAYS_URL, MODULE_NAME, PROTEIN_PATHWAY_URL

__all__ = [
    'get_pathway_df',
    'get_entity_pathway_df',
]


def get_pathway_df(url: Optional[str] = None) -> pd.DataFrame:
    """Convert tab separated txt files to pandas Dataframe.

    :param url: url from KEGG tab separated file
    :return: dataframe of the file
    """
    df = pd.read_csv(
        url or ensure_path(MODULE_NAME, KEGG_PATHWAYS_URL, path='pathways.tsv'),
        sep='\t',
        header=None,
        names=['kegg_pathway_id', 'name'],
    )
    # df['kegg_pathway_id'] = df['kegg_pathway_id'].map(_remove_path_prefix)
    return df


def get_entity_pathway_df(url: Optional[str] = None) -> pd.DataFrame:
    """Convert tab separated text files in to DataFrame.

    :param url: An optional url from a KEGG TSV file
    """
    df = pd.read_csv(
        url or ensure_path(MODULE_NAME, PROTEIN_PATHWAY_URL, path='protein_pathway.tsv'),
        sep='\t',
        header=None,
        names=['kegg_protein_id', 'kegg_pathway_id'],
    )
    # df['kegg_pathway_id'] = df['kegg_pathway_id'].map(_remove_path_prefix)
    return df
