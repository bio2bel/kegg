# -*- coding: utf-8 -*-

"""This module populates the tables of bio2bel_kegg"""

import itertools as itt
from collections import Counter
import json
import logging
from multiprocessing.pool import ThreadPool

import requests
from bio2bel.utils import get_connection
from bio2bel_hgnc.manager import Manager as HgncManager
from pybel.constants import PART_OF, FUNCTION, PROTEIN, BIOPROCESS, NAMESPACE, NAME
from pybel.struct.graph import BELGraph
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from .constants import MODULE_NAME, KEGG, API_KEGG_GET, METADATA_FILE_PATH
from .models import Base, Pathway, Protein
from .parsers import *

__all__ = [
    'Manager'
]

log = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Manager(object):
    """Database manager"""

    def __init__(self, connection=None):
        self.connection = get_connection(MODULE_NAME, connection)
        self.engine = create_engine(self.connection)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.session_maker()
        self.create_all()

    def create_all(self, check_first=True):
        """Create tables for Bio2BEL KEGG"""
        log.info('create table in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self, check_first=True):
        """Drop all tables for Bio2BEL KEGG"""
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

    def query_gene_set(self, gene_set):
        """Returns pathway counter dictionary

        :param list[str] gene_set: gene set to be queried
        :rtype: list[dict]
        :return: Enriched pathways with mapped pathways/total
        """

        proteins = self._query_proteins_in_hgnc_list(gene_set)

        pathways_lists = [
            protein.get_pathways_ids()
            for protein in proteins
        ]

        # Flat the pathways lists and applies Counter to get the number matches in every mapped pathway
        pathway_counter = Counter(itt.chain(*pathways_lists))

        enrichment_results = dict()

        for pathway_kegg_id, proteins_mapped in pathway_counter.items():
            pathway = self.get_pathway_by_id(pathway_kegg_id)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results[pathway.kegg_id] = {
                "pathway_id": pathway.kegg_id,
                "pathway_name": pathway.name,
                "mapped_proteins": proteins_mapped,
                "pathway_size": len(pathway_gene_set),
                "pathway_gene_set": pathway_gene_set,
            }

        return enrichment_results

    def _query_proteins_in_hgnc_list(self, gene_set):
        """Returns the proteins in the database within the gene set query

        :param list[str] gene_set: hgnc symbol lists
        :rtype: list[bio2bel_kegg.models.Protein]
        :return: list of proteins
        """
        return self.session.query(Protein).filter(Protein.hgnc_symbol.in_(gene_set)).all()

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

    def get_all_pathways(self):
        """Gets all pathways stored in the database

        :rtype: list[Pathway]
        """
        return self.session.query(Pathway).all()

    def get_pathway_names_to_ids(self):
        """Returns a dictionary of pathway names to ids

        :rtype: dict[str,str]
        """
        human_pathways = self.get_all_pathways()

        return {
            pathway.name: pathway.kegg_id
            for pathway in human_pathways
        }

    def get_all_hgnc_symbols(self):
        """Returns the set of genes present in all KEGG Pathways

        :rtype: set
        """
        return {
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            for gene in pathway.proteins
            if pathway.proteins
        }

    def get_pathway_size_distribution(self):
        """Returns pathway sizes

        :rtype: dict
        :return: pathway sizes
        """

        pathways = self.get_all_pathways()

        return {
            pathway.name: len(pathway.proteins)
            for pathway in pathways
            if pathway.proteins
        }

    def query_pathway_by_name(self, query, limit=None):
        """Returns all pathways having the query in their names

        :param query: query string
        :param Optional[int] limit: limit result query
        :rtype: list[Pathway]
        """

        q = self.session.query(Pathway).filter(Pathway.name.contains(query))

        if limit:
            q = q.limit(limit)

        return q.all()

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

    def export_genesets(self):
        """Returns pathway - genesets mapping"""
        return {
            pathway.name: {
                protein.hgnc_symbol
                for protein in pathway.proteins
            }
            for pathway in self.session.query(Pathway).all()
        }

    """Methods to populate the DB"""

    def _populate_pathways(self, url=None):
        """Populate pathway table

        :param Optional[str] url: url from pathway table file
        """
        df = get_pathway_names_df(url=url)

        pathways_dict = parse_pathways(df)

        for id, name in tqdm(pathways_dict.items(), desc='Loading pathways'):
            pathway = self.get_or_create_pathway(kegg_id=id, name=name)

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
