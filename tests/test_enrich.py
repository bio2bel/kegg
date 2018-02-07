# -*- coding: utf-8 -*-
""" This module contains tests enrichment of BEL graphs using Bio2BEL KEGG"""

from tests.constants import DatabaseMixin, enrichment_graph


class TestEnrich(DatabaseMixin):
    """Tests the enrichment of module"""

    def test_get_pathway_graph(self):
        graph = self.manager.get_pathway_graph('path:hsa00030')

        self.assertEqual(15, graph.number_of_nodes())  # 14 proteins + pathway node
        self.assertEqual(14, graph.number_of_edges())  # 14 edges protein -- pathway

    def test_enrich_kegg_pathway(self):
        graph_example = enrichment_graph()

        self.manager.enrich_kegg_pathway(graph_example)

        # 14 proteins in the pathway + gene of one of the proteins + pathway node
        self.assertEqual(16, graph_example.number_of_nodes())
        self.assertEqual(17, graph_example.number_of_edges())  # 14 edges protein -- pathway + 3 other relationships

    def test_enrich_kegg_protein(self):
        graph_example = enrichment_graph()

        self.manager.enrich_kegg_protein(graph_example)

        self.assertEqual(5, graph_example.number_of_nodes())  # 2 proteins + gene + pathway + new pathway
        self.assertEqual(6, graph_example.number_of_edges())  # 3 edges + new one
