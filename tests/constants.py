# -*- coding: utf-8 -*-

"""Test constants for Bio2BEL KEGG."""

import logging
import os

import bio2bel_hgnc
from bio2bel.testing import TemporaryConnectionMixin
from bio2bel_kegg.constants import HGNC, KEGG
from bio2bel_kegg.manager import Manager
from pybel.constants import DECREASES, INCREASES, PART_OF, RELATION
from pybel.dsl import bioprocess, gene, protein
from pybel.struct.graph import BELGraph

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
resources_path = os.path.join(dir_path, 'resources')

pathways = os.path.join(resources_path, 'hsa.txt')
protein_pathway_url = os.path.join(resources_path, 'pathway_gene.txt')

hgnc_test_path = os.path.join(resources_path, 'hgnc_test.json')
hcop_test_path = os.path.join(resources_path, 'hcop_test.txt')


class DatabaseMixin(TemporaryConnectionMixin):
    """A test case with a populated database."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary database."""
        super().setUpClass()

        # create temporary database
        cls.manager = Manager(cls.connection)

        cls.hgnc_manager = bio2bel_hgnc.Manager(connection=cls.connection)
        cls.hgnc_manager.create_all()
        cls.hgnc_manager.populate(
            hgnc_file_path=hgnc_test_path,
            hcop_file_path=hcop_test_path,
        )

        # fill temporary database with test data
        cls.manager.populate(
            pathways_url=pathways,
            protein_pathway_url=protein_pathway_url
        )

    @classmethod
    def tearDownClass(cls):
        """Close the connection in the manager and deletes the temporary database."""
        cls.manager.drop_all()
        cls.hgnc_manager.drop_all()
        cls.manager.session.close()
        cls.hgnc_manager.session.close()
        super().tearDownClass()


protein_a = protein(namespace=HGNC, name='GPI')
protein_b = protein(namespace=HGNC, name='PFKP')
gene_c = gene(namespace=HGNC, name='PGLS')
pathway_a = bioprocess(namespace=KEGG, name='Pentose phosphate pathway - Homo sapiens (human)')


def enrichment_graph():
    """Build a test graph with 2 proteins, one gene, and one kegg pathway all contained in HGNC.

    :rtype: BELGraph
    """
    graph = BELGraph(
        name='My test graph for enrichment',
        version='0.0.1'
    )

    protein_a_tuple = graph.add_node_from_data(protein_a)
    protein_b_tuple = graph.add_node_from_data(protein_b)
    gene_c_tuple = graph.add_node_from_data(gene_c)
    pathway_a_tuple = graph.add_node_from_data(pathway_a)

    graph.add_edge(protein_a_tuple, protein_b_tuple, attr_dict={
        RELATION: INCREASES,
    })

    graph.add_edge(protein_b_tuple, gene_c_tuple, attr_dict={
        RELATION: DECREASES,
    })

    graph.add_edge(gene_c_tuple, pathway_a_tuple, attr_dict={
        RELATION: PART_OF,
    })

    return graph
