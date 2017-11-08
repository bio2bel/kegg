# -*- coding: utf-8 -*-

"""
This module parsers the KEGG pathway names file

The "Complete list of pathways" file maps the KEGG identifiers to their corresponding pathway name .

"""
import pandas as pd

from bio2bel_kegg.constants import KEGG_PATHWAYS_URL

__all__ = [
    'get_pathway_names_df',
    'parse_pathways',
]


def get_pathway_names_df(url=None):
    """ Converts tab separated txt files to pandas Dataframe

    :param Optional[str] url: url from KEGG tab separated file
    :return: dataframe of the file
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(
        url or KEGG_PATHWAYS_URL,
        sep='\t',
        header=None
    )
    return df


def parse_pathways(pathway_dataframe):
    """ Parser the pathway table dataframe

    :param pandas.DataFrame pathway_dataframe: Pathway hierarchy as dataframe
    :rtype: dict
    :return Object representation dictionary (kegg_id: name, species)
    """

    pathways = {
        kegg_id: name
        for line, (kegg_id, name) in pathway_dataframe.iterrows()
    }

    return pathways
