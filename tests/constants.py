# -*- coding: utf-8 -*-

"""Test constants for Bio2BEL KEGG."""

import logging
import os

from bio2bel.testing import TemporaryConnectionMixin
from bio2bel_kegg.constants import HGNC, KEGG
from bio2bel_kegg.manager import Manager
from pybel.dsl import bioprocess, gene, protein
from pybel.struct.graph import BELGraph

logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIRECTORY = os.path.join(dir_path, 'resources')

test_pathways_path = os.path.join(RESOURCES_DIRECTORY, 'hsa.txt')
test_proteins_path = os.path.join(RESOURCES_DIRECTORY, 'pathway_gene.txt')

test_protein_path = os.path.join(RESOURCES_DIRECTORY, 'test_protein.txt')
test_pathway_path = os.path.join(RESOURCES_DIRECTORY, 'test_pathway.txt')


class DatabaseMixin(TemporaryConnectionMixin):
    """A test case with a populated database."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary database."""
        super().setUpClass()

        # create temporary database
        cls.manager = Manager(cls.connection)

        # fill temporary database with test data
        cls.manager.populate(
            pathways_url=test_pathways_path,
            protein_pathway_url=test_proteins_path,
        )

    @classmethod
    def tearDownClass(cls):
        """Close the connection in the manager and deletes the temporary database."""
        cls.manager.drop_all()
        cls.manager.session.close()
        super().tearDownClass()


protein_a = protein(namespace=HGNC, identifier='4458', name='GPI')
protein_b = protein(namespace=HGNC, identifier='8878', name='PFKP')
gene_c = gene(namespace=HGNC, identifier='8903', name='PGLS')
pathway_a = bioprocess(namespace=KEGG, identifier='hsa00030', name='Pentose phosphate pathway - Homo sapiens (human)')


def enrichment_graph() -> BELGraph:
    """Build a test graph with 2 proteins, one gene, and one kegg pathway all contained in HGNC."""
    graph = BELGraph(
        name='My test graph for enrichment',
        version='0.0.1',
    )
    graph.add_directly_increases(protein_a, protein_b, citation='1234', evidence='asgag')
    graph.add_decreases(protein_b, gene_c, citation='1234', evidence='asgag')
    graph.add_part_of(gene_c, pathway_a)
    return graph
