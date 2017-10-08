# -*- coding: utf-8 -*-

"""
This module parsers the Kegg pathway names file

The "Complete list of pathways" file maps the Kegg identifiers to their corresponding pathway name .

"""


def parser_pathways(pathway_dataframe):
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
