# -*- coding: utf-8 -*-

"""This module populates the tables of bio2bel_kegg"""

import json
import logging
from multiprocessing.pool import ThreadPool

import requests
from pybel.constants import BIOPROCESS, FUNCTION, NAME, NAMESPACE, PART_OF, PROTEIN
from tqdm import tqdm

from bio2bel import bio2bel_populater
from bio2bel_hgnc.manager import Manager as HgncManager
from compath_utils import CompathManager
from pybel.struct.graph import BELGraph
from .constants import API_KEGG_GET, KEGG, METADATA_FILE_PATH, MODULE_NAME
from .models import Base, Pathway, Protein
from .parsers import *

__all__ = [
    'Manager'
]

log = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Manager(CompathManager):
    """Database manager"""

    module_name = MODULE_NAME
    flask_admin_models = [Pathway, Protein]
    pathway_model = Pathway
    protein_model = Protein
    pathway_model_identifier_column = Pathway.kegg_id

    @property
    def base(self):
        return Base

    def get_or_create_pathway(self, kegg_id, name=None):
        """Gets an pathway from the database or creates it

        :param str kegg_id: kegg identifier
        :param Optional[str] name: name of the pathway
        :rtype: Pathway
        """
        pathway = self.get_pathway_by_id(kegg_id)

        if pathway is None:
            pathway = Pathway(
                kegg_id=kegg_id,
                name=name
            )
            self.session.add(pathway)

        return pathway

    def get_protein_by_kegg_id(self, kegg_id):
        """Gets a protein by its kegg id

        :param kegg_id: kegg identifier
        :rtype: Optional[Protein]
        """
        return self.session.query(Protein).filter(Protein.kegg_id == kegg_id).one_or_none()

    def get_protein_by_hgnc_id(self, hgnc_id):
        """Gets a protein by its hgnc_id

        :param hgnc_id: hgnc_id
        :rtype: Optional[Protein]
        """
        return self.session.query(Protein).filter(Protein.hgnc_id == hgnc_id).one_or_none()

    def get_protein_by_hgnc_symbol(self, hgnc_symbol):
        """Gets a protein by its hgnc symbol

        :param hgnc_id: hgnc identifier
        :rtype: Optional[Protein]
        """
        return self.session.query(Protein).filter(Protein.hgnc_symbol == hgnc_symbol).one_or_none()

    """Methods to populate the DB"""

    def _populate_pathways(self, url=None):
        """Populate pathway table

        :param Optional[str] url: url from pathway table file
        """
        df = get_pathway_names_df(url=url)

        pathways_dict = parse_pathways(df)

        for kegg_id, name in tqdm(pathways_dict.items(), desc='Loading pathways'):
            self.get_or_create_pathway(kegg_id=kegg_id, name=name)

        self.session.commit()

    def _pathway_entity(self, url=None, metadata_existing=None):
        """Populates Protein Tables

        :param Optional[str] url: url from protein to pathway file
        """
        protein_df = get_entity_pathway_df(url=url)

        protein_description_urls = create_entity_description_url(protein_df, API_KEGG_GET)

        hgnc_manager = HgncManager(connection=self.connection)

        hgnc_id_to_symbol = hgnc_manager.build_hgnc_id_symbol_mapping()

        if not metadata_existing:
            # KEGG protein ID to Protein model attributes dictionary
            pid_attributes = {}

            log.info('Fetching all protein meta-information (needs around 7300 iterations).'
                     'You can modify the numbers of request by modifying ThreadPool to make this faster. '
                     'However, the KEGG RESTful API might reject a big amount of requests.')

            # Multi-thread processing of protein description requests
            results = ThreadPool(1).imap_unordered(requests.get, protein_description_urls)
            for result in tqdm(results, desc='Fetching meta information'):
                kegg_protein_id = result.url.rsplit('/', 1)[-1]

                protein_dict = process_protein_info_to_model(result)

                # Adds HGNC id information
                if 'hgnc_id' in protein_dict:
                    # Add extra fields to the protein dictionary
                    protein_dict['hgnc_symbol'] = hgnc_id_to_symbol.get(protein_dict['hgnc_id'])

                protein_dict['kegg_id'] = kegg_protein_id

                # KEGG protein ID to Protein object already created
                pid_attributes[kegg_protein_id] = protein_dict

            with open(METADATA_FILE_PATH, 'w') as outfile:
                json.dump(pid_attributes, outfile)

        else:
            log.info('Loading existing metadata file')
            pid_attributes = json.load(open(METADATA_FILE_PATH))

        log.info('Done fetching')

        pid_protein = {}

        for kegg_protein_id, kegg_pathway_id in tqdm(parse_entity_pathway(protein_df), desc='Loading proteins'):

            if kegg_protein_id in pid_protein:
                protein = pid_protein[kegg_protein_id]
            else:
                try:
                    protein = Protein(**pid_attributes[kegg_protein_id])
                except KeyError:
                    log.error('Protein key not found. This might be due to an old cached metadata file. '
                              'Please delete the file {} and try again.'.format(METADATA_FILE_PATH))
                    raise

                pid_protein[kegg_protein_id] = protein
                self.session.add(protein)

            pathway = self.get_pathway_by_id(kegg_pathway_id)
            protein.pathways.append(pathway)
        self.session.commit()

    @bio2bel_populater(MODULE_NAME)
    def populate(self, pathways_url=None, protein_pathway_url=None, metadata_existing=False):
        """Populates all tables"""

        self._populate_pathways(url=pathways_url)
        self._pathway_entity(url=protein_pathway_url, metadata_existing=metadata_existing)

    def get_pathway_graph(self, kegg_id):
        """Returns a new graph corresponding to the pathway
        :param str kegg_id: kegg identifier
        :rtype: pybel.BELGraph
        :return: Graph
        """

        pathway = self.get_pathway_by_id(kegg_id)

        graph = BELGraph(
            name='{} graph'.format(pathway.name),
        )

        pathway_node = pathway.serialize_to_pathway_node()

        for protein in pathway.proteins:
            graph.add_qualified_edge(
                pathway_node,
                protein.serialize_to_protein_node(),
                relation=PART_OF,
                citation='27899662',
                evidence='http://www.genome.jp/kegg/'
            )

        return graph

    def enrich_kegg_pathway(self, graph):
        """Enrich all proteins belonging to kegg pathway nodes in the graph

        :param pybel.BELGraph graph: A BEL Graph
        """
        for node, data in graph.nodes(data=True):
            if data[FUNCTION] == BIOPROCESS and data[NAMESPACE] == KEGG and NAME in data:
                pathway = self.get_pathway_by_name(data[NAME])

                for protein in pathway.proteins:
                    graph.add_qualified_edge(
                        protein.serialize_to_protein_node(),
                        node,
                        relation=PART_OF,
                        citation='27899662',
                        evidence='http://www.genome.jp/kegg/'
                    )

    def enrich_kegg_protein(self, graph):
        """Enrich all kegg pathways associated with proteins in the graph

        :param pybel.BELGraph graph: A BEL Graph
        """
        for node, data in graph.nodes(data=True):
            if data[FUNCTION] == PROTEIN and data[NAMESPACE] == 'HGNC':
                protein = self.get_protein_by_hgnc_symbol(data[NAME])

                for pathway in protein.pathways:
                    graph.add_qualified_edge(
                        node,
                        pathway.serialize_to_pathway_node(),
                        relation=PART_OF,
                        citation='27899662',
                        evidence='http://www.genome.jp/kegg/'
                    )

    def _add_admin(self, app, **kwargs):
        from flask_admin import Admin
        from flask_admin.contrib.sqla import ModelView
        class PathwayView(ModelView):
            """Pathway view in Flask-admin"""
            column_searchable_list = (
                Pathway.kegg_id,
                Pathway.name
            )

        class ProteinView(ModelView):
            """Protein view in Flask-admin"""
            column_searchable_list = (
                Protein.kegg_id,
                Protein.uniprot_id,
                Protein.hgnc_id
            )

        admin = Admin(app, **kwargs)
        admin.add_view(PathwayView(Pathway, self.session))
        admin.add_view(ProteinView(Protein, self.session))
        return admin
