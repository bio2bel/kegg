# -*- coding: utf-8 -*-

"""
This module populates the tables of bio2bel_kegg
"""

import logging

from bio2bel.utils import get_connection
from pybel.constants import PART_OF, FUNCTION, PROTEIN, BIOPROCESS, NAMESPACE, NAME
from pybel.struct.graph import BELGraph
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from bio2bel_kegg.constants import MODULE_NAME, DBLINKS, PROTEIN_RESOURCES, KEGG
from bio2bel_kegg.hgnc_connection import symbol_to_hgnc_id
from bio2bel_kegg.models import Base, Pathway, Protein
from bio2bel_kegg.parsers import *

log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, connection=None):
        self.connection = get_connection(MODULE_NAME, connection)
        self.engine = create_engine(self.connection)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.session_maker()
        self.create_all()

    def create_all(self, check_first=True):
        """Create tables"""
        log.info('create table in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self, check_first=True):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine, checkfirst=check_first)

    @staticmethod
    def ensure(connection=None):
        """Checks and allows for a Manager to be passed to the function. """
        if connection is None or isinstance(connection, str):
            return Manager(connection=connection)

        if isinstance(connection, Manager):
            return connection

        raise TypeError

    """Custom query methods"""

    def get_pathway_by_id(self, kegg_id):
        """Gets a pathway by its kegg id
        :param kegg_id: kegg identifier
        :rtype: Optional[Pathway]
        """
        return self.session.query(Pathway).filter(Pathway.kegg_id == kegg_id).one_or_none()

    def get_pathway_by_name(self, pathway_name):
        """Gets a pathway by its kegg id
        :param pathway_name: kegg name
        :rtype: Optional[Pathway]
        """
        return self.session.query(Pathway).filter(Pathway.name == pathway_name).one_or_none()

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
        """Gets a protein by its hgnc id
        :param hgnc_id: hgnc identifier
        :rtype: Optional[Protein]
        """
        return self.session.query(Protein).filter(Protein.hgnc_id == hgnc_id).one_or_none()

    def get_protein_by_hgnc_symbol(self, hgnc_symbol):
        """Gets a protein by its hgnc symbol
        :param hgnc_id: hgnc identifier
        :rtype: Optional[Protein]
        """
        hgnc_id = symbol_to_hgnc_id[hgnc_symbol]

        return self.session.query(Protein).filter(Protein.hgnc_id == hgnc_id).one_or_none()

    """Methods to populate the DB"""

    def _populate_pathways(self, url=None):
        """ Populate pathway table

        :param Optional[str] url: url from pathway table file
        """
        df = get_pathway_names_df(url=url)

        pathways_dict = parse_pathways(df)

        for id, name in tqdm(pathways_dict.items(), desc='Loading pathways'):
            pathway = self.get_or_create_pathway(kegg_id=id, name=name)

        self.session.commit()

    def _pathway_entity(self, url=None):
        """ Populates Protein Tables

        :param Optional[str] url: url from protein to pathway file
        """
        protein_df = get_entity_pathway_df(url=url)

        pid_protein = {}

        for kegg_protein_id, kegg_pathway_id in tqdm(parse_entity_pathway(protein_df), desc='Loading proteins'):

            if kegg_protein_id in pid_protein:
                protein = pid_protein[kegg_protein_id]
            else:

                # Get protein description from KEGG API
                description = parse_description(kegg_protein_id)
                # Filters out db link columns
                protein_columns = get_description_properties(
                    description=description,
                    description_property=DBLINKS,
                    columns=PROTEIN_RESOURCES
                )

                # Adapt the dict keys to match protein model columns
                protein_columns = kegg_properties_to_models(protein_columns)

                protein_columns['kegg_id'] = kegg_protein_id
                protein = Protein(**protein_columns)
                pid_protein[kegg_protein_id] = protein
                self.session.add(protein)

            pathway = self.get_or_create_pathway(kegg_pathway_id)
            protein.pathways.append(pathway)
        self.session.commit()

    def populate(self, pathways_url=None, protein_pathway_url=None):
        """ Populates all tables"""
        self._populate_pathways(url=pathways_url)
        self._pathway_entity(url=protein_pathway_url)

    def get_pathway_graph(self, kegg_id):
        """Returns a new graph corresponding to the pathway"""

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

        :param graph: A BEL Graph
        :type graph: pybel.BELGraph
        :type graph: pybel.BELGraph
        :return graph: A BEL Graph
        """

        for node, data in graph.nodes(data=True):

            if data[FUNCTION] == BIOPROCESS and data[NAMESPACE] == KEGG:

                pathway = self.get_pathway_by_name(data[NAME])

                for protein in pathway.proteins:
                    graph.add_qualified_edge(
                        protein.serialize_to_protein_node(),
                        node,
                        relation=PART_OF,
                        citation='27899662',
                        evidence='http://www.genome.jp/kegg/'
                    )

        return graph

    def enrich_kegg_protein(self, graph):
        """Enrich all kegg pathways associated with proteins in the graph

        :param graph: A BEL Graph
        :type graph: pybel.BELGraph
        :type graph: pybel.BELGraph
        :return graph: A BEL Graph
        """

        for node, data in graph.nodes(data=True):

            if data[FUNCTION] == PROTEIN and data[NAMESPACE] == 'HGNC':

                protein = self.get_protein_by_hgnc_id(symbol_to_hgnc_id[data[NAME]])

                for pathway in protein.pathways:
                    graph.add_qualified_edge(
                        node,
                        pathway.serialize_to_pathway_node(),
                        relation=PART_OF,
                        citation='27899662',
                        evidence='http://www.genome.jp/kegg/'
                    )

        return graph
