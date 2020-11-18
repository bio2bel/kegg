# -*- coding: utf-8 -*-

"""Test for the parser and database."""

from bio2bel_kegg.models import Pathway, Protein
from tests.constants import DatabaseMixin, enrichment_graph


class TestParse(DatabaseMixin):
    """Tests the parsing module."""

    def test_pathway_count(self):
        """Test number of pathways created."""
        pathway_number = self.manager.session.query(Pathway).count()
        self.assertEqual(9, pathway_number)

    def test_protein_count(self):
        """Test number of proteins created."""
        protein_number = self.manager.session.query(Protein).count()
        self.assertEqual(29, protein_number)

    def test_pathway_protein_1(self):
        """Test number of pathways in pathway."""
        pathway = self.manager.get_pathway_by_id('hsa00030')
        self.assertIsNotNone(pathway, msg='Unable to find pathway')
        self.assertEqual(14, len(pathway.proteins))

    def test_pathway_protein_2(self):
        """Test number of pathways in pathway."""
        pathway = self.manager.get_pathway_by_id('hsa00010')
        self.assertIsNotNone(pathway, msg='Unable to find pathway')
        self.assertEqual(16, len(pathway.proteins))

    def test_protein_pathway_1(self):
        """Test number of pathways in pathway."""
        protein = self.manager.session.query(Protein).filter(Protein.kegg_id == 'hsa:5214').one_or_none()
        self.assertIsNotNone(protein, msg='Unable to find pathway')
        self.assertEqual(2, len(protein.pathways))
        self.assertEqual(
            {'hsa00030', 'hsa00010'},
            {
                pathway.identifier
                for pathway in protein.pathways
            },
        )

        self.assertEqual(
            {'Pentose phosphate pathway - Homo sapiens (human)', 'Glycolysis / Gluconeogenesis - Homo sapiens (human)'},
            {
                pathway.name
                for pathway in protein.pathways
            },
        )

    def test_gene_query_1(self):
        """Single protein query. This protein is associated with 2 pathways."""
        enriched_pathways = self.manager.query_hgnc_symbols(['PFKP'])
        self.assertIsNotNone(enriched_pathways, msg='Enriching function is not working')

        self.assertIn("hsa00030", enriched_pathways)
        self.assertEqual(
            {
                "pathway_id": "hsa00030",
                "pathway_name": "Pentose phosphate pathway - Homo sapiens (human)",
                "mapped_proteins": 1,
                "pathway_size": 14,
                "pathway_gene_set": {
                    'ALDOA',
                    'ALDOB',
                    'ALDOC',
                    'DERA',
                    'G6PD',
                    'GPI',
                    'IDNK',
                    'PFKL',
                    'PFKM',
                    'PFKP',
                    'PGD',
                    'PGLS',
                    'PGM1',
                    'RPIA',
                },
            },
            enriched_pathways["hsa00030"],
        )

        self.assertIn("hsa00010", enriched_pathways)

    def test_gene_query_2(self):
        """Multiple protein query."""
        enriched_pathways = self.manager.query_hgnc_symbols(['PFKP', 'GPI'])  # hsa:5214 and hsa:2821
        self.assertIsNotNone(enriched_pathways, msg='Enriching function is not working')

        self.assertIn("hsa00010", enriched_pathways)
        self.assertEqual(1, enriched_pathways['hsa00010']['mapped_proteins'])

        self.assertEqual(
            {
                "pathway_id": "hsa00030",
                "pathway_name": "Pentose phosphate pathway - Homo sapiens (human)",
                "mapped_proteins": 2,
                "pathway_size": 14,
                "pathway_gene_set": {
                    'ALDOA',
                    'ALDOB',
                    'ALDOC',
                    'DERA',
                    'G6PD',
                    'GPI',
                    'IDNK',
                    'PFKL',
                    'PFKM',
                    'PFKP',
                    'PGD',
                    'PGLS',
                    'PGM1',
                    'RPIA',
                },
            },
            enriched_pathways["hsa00030"],
        )

    def test_gene_query_3(self):
        """Multiple protein query."""
        enriched_pathways = self.manager.query_hgnc_symbols(['PFKP', 'PGD'])  # hsa:5214 and hsa:5226
        self.assertIsNotNone(enriched_pathways, msg='Enriching function is not working')

        self.assertIn("hsa00010", enriched_pathways)
        self.assertEqual(1, enriched_pathways['hsa00010']['mapped_proteins'])

        self.assertIn("hsa00030", enriched_pathways)
        self.assertEqual(2, enriched_pathways['hsa00030']['mapped_proteins'])

    def test_get_pathway_graph(self):
        """Test pathway creation."""
        graph = self.manager.get_pathway_graph('hsa00030')

        self.assertEqual(15, graph.number_of_nodes())  # 14 proteins + pathway node
        self.assertEqual(14, graph.number_of_edges())  # 14 edges protein -- pathway

    def test_enrich_kegg_pathway(self):
        """Test graph enrichment."""
        graph_example = enrichment_graph()

        self.manager.enrich_pathways(graph_example)

        # 14 proteins in the pathway + gene of one of the proteins + pathway node
        self.assertEqual(16, graph_example.number_of_nodes())
        self.assertEqual(17, graph_example.number_of_edges())  # 14 edges protein -- pathway + 3 other relationships

    def test_enrich_kegg_protein(self):
        """Test pathway protein enrichmnent."""
        graph_example = enrichment_graph()

        self.manager.enrich_proteins(graph_example)

        # TODO revisit this test
        self.assertEqual(32, graph_example.number_of_nodes())
        self.assertEqual(33, graph_example.number_of_edges())
