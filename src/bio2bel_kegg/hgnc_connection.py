# -*- coding: utf-8 -*-

"""This modules loads the dictionaries necessaries for mapping hgnc symbols to their ids and vice versa using Bio2bel_hgnc."""

from bio2bel_hgnc.manager import Manager as bio2bel_hgnc_manager

manager = bio2bel_hgnc_manager()

hgnc_id_to_symbol = manager.build_hgnc_id_symbol_mapping()
symbol_to_hgnc_id = manager.build_hgnc_symbol_id_mapping()