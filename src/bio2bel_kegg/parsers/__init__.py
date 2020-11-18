# -*- coding: utf-8 -*-

"""This module contains multiple parsers for the KEGG public data sources."""

from .description import process_protein_info_to_model  # noqa: F401
from .entities import get_entity_pathway_df, parse_entity_pathway  # noqa: F401
from .pathways import get_pathway_names_df, parse_pathways  # noqa: F401
