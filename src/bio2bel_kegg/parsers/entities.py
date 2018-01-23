# -*- coding: utf-8 -*-

"""
This module parsers the KEGG pathway entities file

"""
import pandas as pd

from bio2bel_kegg.constants import PROTEIN_PATHWAY_URL

__all__ = [
    'get_entity_pathway_df',
    'parse_entity_pathway',
    'create_entity_description_url'
]


def get_entity_pathway_df(url=None):
    """ Converts tab separated txt files to pandas Dataframe

    :param Optional[str] url: url from KEGG tab separated file
    :return: dataframe of the file
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(
        url or PROTEIN_PATHWAY_URL,
        sep='\t',
        header=None
    )
    return df


def parse_entity_pathway(pathway_dataframe):
    """ Parser the pathway-entity table dataframe

    :param pandas.DataFrame pathway_dataframe: Pathway hierarchy as dataframe
    :rtype: list[tuple]
    :return association list [(entity, pathway)]
    """

    pathways = [
        (entity, pathway)
        for line, (entity, pathway) in pathway_dataframe.iterrows()
    ]

    return pathways


def create_entity_description_url(pathway_dataframe, baseurl):
    """ Returns all entities in entity pathway dataframe

    :param pandas.DataFrame pathway_dataframe: Pathway hierarchy as dataframe
    :param str baseurl: base url
    :rtype: set
    :return all entities
    """

    return {
        baseurl.format(entity)
        for line, (entity, pathway) in pathway_dataframe.iterrows()
    }
