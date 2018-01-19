# -*- coding: utf-8 -*-

"""
This module parsers the description files -> http://rest.kegg.jp/get/ in KEGG RESTful API

"""

import re
import logging
import requests

from bio2bel_kegg.constants import API_KEGG_GET

__all__ = [
    'parse_entry_line',
    'remove_first_word',
    'get_first_word',
    'parse_pathway_line',
    'parse_link_line',
    'parse_description',
    'get_description_properties',
    'kegg_properties_to_models',
]

logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_entry_line(line):
    """ Parse entry line to tuple

    :param line:
    :rtype tuple
    :return: tuple of entry
    """
    return tuple(
        [line.strip(' ')
         for line in line.split()[1:]
         ]
    )


def remove_first_word(string):
    """ Remove the first word of the line

    :param str string: string
    :rtype str
    :return: string without the first word
    """
    return string.split(' ', 1)[1].strip()


def get_first_word(string):
    """ Get the first word of the line

    :param str string: string
    :rtype str
    :return: string with the first word
    """
    return string.split(' ', 1)[0]


def parse_pathway_line(line):
    """ Parse entry pathway line to tuple

    :param line:
    :rtype tuple
    :return: tuple of entry
    """

    line = remove_first_word(line)

    return tuple(
        line.strip(' ')
        for line in re.split(r'\s{2,}', line)
    )


def parse_link_line(line):
    """ Parse entry dblink line to tuple

    :param line:
    :rtype tuple
    :return: tuple of entry
    """

    line = remove_first_word(line)

    column, link_id = line.split(":")

    return (column.strip(), link_id.strip())


def parse_description(identifier):
    """ Parse the several properties in the description file given an KEGG identifier using the KEGG API
    Properties parsed:
    - ENTRY
    - PATHWAY
    - DBLINKS

    :param str identifier: id for the query
    :rtype: dict
    :return: description dictionary
    """

    r = requests.get(API_KEGG_GET.format(identifier), stream=True)

    description = {}

    for line in r.iter_lines():
        line = line.decode('utf-8')

        if not line.startswith(' '):
            keyword = get_first_word(line)

        if keyword == 'ENTRY':
            description['ENTRY'] = parse_entry_line(line)

        elif keyword == 'PATHWAY':

            if 'PATHWAY' not in description:
                description['PATHWAY'] = [parse_pathway_line(line)]
            else:
                description['PATHWAY'].append(parse_pathway_line(line))

        elif keyword == 'DBLINKS':

            if 'DBLINKS' not in description:
                description['DBLINKS'] = [parse_link_line(line)]
            else:
                description['DBLINKS'].append(parse_link_line(line))

    return description


def get_description_properties(description, description_property, columns):
    """Gets specific description properties

    :param dict protein_description: id for the query
    :param str description_property: main property in the description
    :param list columns: columns to be filtered
    :rtype: dict
    :return: description dictionary

    """
    return {
        pair[0]: pair[1]
        for pair in description[description_property]
        if pair[0] in columns
    }


def kegg_properties_to_models(kegg_attributes):
    """Modifies the kegg attribute dictionary to match the db '{}_id' formatting

    :param dict kegg_attributes: kegg description dictionary
    :rtype: dict
    :return: dictionary with bio2bel_kegg adapted keys
    """

    return {
        '{}_id'.format(key.lower()): value
        for key, value in kegg_attributes.items()
    }
