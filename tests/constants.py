# -*- coding: utf-8 -*-
""" This module contains all test constants"""

import os
import tempfile
import unittest

from bio2bel_kegg.constants import HGNC, KEGG
from bio2bel_kegg.manager import Manager

dir_path = os.path.dirname(os.path.realpath(__file__))
resources_path = os.path.join(dir_path, 'resources')

pathways = os.path.join(resources_path, 'hsa.txt')
protein_pathway_url = os.path.join(resources_path, 'pathway_gene.txt')

from pybel.struct.graph import BELGraph
from pybel.constants import *


class DatabaseMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create temporary file"""

        cls.fd, cls.path = tempfile.mkstemp()
        cls.connection = 'sqlite:///' + cls.path

        # create temporary database
        cls.manager = Manager(cls.connection)
        cls.manager.create_all()
        # fill temporary database with test data
        cls.manager.populate(
            pathways_url=pathways,
            protein_pathway_url=protein_pathway_url
        )

    @classmethod
    def tearDownClass(cls):
        """Closes the connection in the manager and deletes the temporary database"""
        cls.manager.session.close()
        os.close(cls.fd)
        os.remove(cls.path)


protein_a = PROTEIN, HGNC, 'GPI'
protein_b = PROTEIN, HGNC, 'PFKP'
gene_c = GENE, HGNC, 'PGLS'
pathway_a = BIOPROCESS, KEGG, 'Pentose phosphate pathway - Homo sapiens (human)'


def enrichment_graph():
    """Simple test graph with 2 proteins, one gene, and one kegg pathway all contained in HGNC"""

    graph = BELGraph(**{
        GRAPH_METADATA: {
            METADATA_VERSION: '1.0.0',
            METADATA_NAME: 'network_test',
            METADATA_DESCRIPTION: 'network for kegg enrichment test',
            METADATA_AUTHORS: 'Fraunhofer SCAI',
            METADATA_CONTACT: 'test@scai.fraunhofer.de',
        }
    })

    graph.add_edge(protein_a, protein_b, attr_dict={
        RELATION: INCREASES,
    })

    graph.add_edge(protein_b, gene_c, attr_dict={
        RELATION: DECREASES,
    })

    graph.add_edge(gene_c, pathway_a, attr_dict={
        RELATION: PART_OF,
    })

    return graph
