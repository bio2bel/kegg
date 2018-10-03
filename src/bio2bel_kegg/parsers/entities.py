# -*- coding: utf-8 -*-

"""This module parsers the KEGG pathway entities file."""

from typing import List, Optional, Tuple

import pandas as pd

from bio2bel_kegg.constants import PROTEIN_PATHWAY_URL

__all__ = [
    'get_entity_pathway_df',
    'parse_entity_pathway',
]


def get_entity_pathway_df(url: Optional[str] = None) -> pd.DataFrame:
    """Convert tab separated text files in to DataFrame.

    :param url: An optional url from a KEGG TSV file
    """
    return pd.read_csv(
        url or PROTEIN_PATHWAY_URL,
        sep='\t',
        header=None
    )


def parse_entity_pathway(pathway_dataframe: pd.DataFrame) -> List[Tuple[str, str]]:
    """Parse the pathway-entity table dataframe.

    :param pathway_dataframe: Pathway hierarchy as dataframe
    :return association list [(entity, pathway)]
    """
    return [
        (entity, pathway)
        for line, (entity, pathway) in pathway_dataframe.iterrows()
    ]
