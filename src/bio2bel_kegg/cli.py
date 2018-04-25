# -*- coding: utf-8 -*-


import logging
import os

import click
from pandas import DataFrame, Series

from bio2bel_kegg.manager import Manager

log = logging.getLogger(__name__)

main = Manager.get_cli()


@main.command()
@click.pass_obj
def export(manager):
    """Export all pathway - gene info to a excel file"""

    log.info("Querying the database")

    # https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
    genesets = DataFrame(
        dict([
            (k, Series(list(v)))
            for k, v in manager.export_genesets().items()
        ])
    )

    log.info("Geneset exported to '{}/kegg_gene_sets.xlsx'".format(os.getcwd()))

    genesets.to_excel('kegg_gene_sets.xlsx', index=False)


if __name__ == '__main__':
    main()
