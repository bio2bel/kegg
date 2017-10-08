# -*- coding: utf-8 -*-

"""
This module parsers the Kegg pathway entities file

"""


def parser_entity(pathway_dataframe):
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
