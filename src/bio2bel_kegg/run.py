# -*- coding: utf-8 -*-

from __future__ import print_function

import logging

import pandas as pd
from pybel.constants import NAMESPACE_DOMAIN_BIOPROCESS
from pybel_tools.definition_utils import write_namespace
from pybel_tools.resources import get_today_arty_namespace, deploy_namespace

log = logging.getLogger(__name__)

MODULE_NAME = 'kegg'


def get_data(url):
    """ Converts tab separated txt files to pandas Dataframe

    :param url: url from kegg tab separated file
    :return: dataframe of the file
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(url, sep='\t', header=None)
    return df


def get_values(df=None):
    """Gets the unique names from Kegg pathway names table. Combines all species.

    :rtype: set[str]
    """
    if df is None:
        df = get_data('FIXME') #TODO: add url

    values = set(df[1])

    return values


def write_belns(file=None):
    """Prints the Kegg Pathway names BEL namespace

    :param file file: A writable file or file-like. Defaults to standard out
    """
    values = get_values()

    write_namespace(
        namespace_name="Kegg Pathway Names",
        namespace_keyword="Kegg",
        namespace_domain=NAMESPACE_DOMAIN_BIOPROCESS,
        author_name='Charles Tapley Hoyt',
        citation_name='FIXME',
        values=values,
        namespace_species='9606',
        namespace_description="Reactome Pathways",
        author_copyright='Creative Commons by 4.0',
        functions="B",
        author_contact="charles.hoyt@scai.fraunhofer.de",
        file=file
    )


def deploy_to_arty(quit_fail_redeploy=True):
    """Gets the data, writes BEL namespace, and writes BEL knowledge to Artifactory"""

    file_name = get_today_arty_namespace(MODULE_NAME)

    with open(file_name, 'w') as file:
        write_belns(file)

    namespace_deploy_success = deploy_namespace(file_name, MODULE_NAME)

    if not namespace_deploy_success and quit_fail_redeploy:
        log.warning('did not redeploy')
        return False
