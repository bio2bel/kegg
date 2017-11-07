# -*- coding: utf-8 -*-
""" This module contains tests for parsing KEGG files"""

from bio2bel_kegg.models import Pathway, Protein
from tests.constants import DatabaseMixin


class TestParse(DatabaseMixin):
    """Tests the parsing module"""

    def test_pathway_count(self):
        pathway_number = self.manager.session.query(Pathway).count()
        self.assertEqual(9, pathway_number)

    def test_protein_count(self):
        protein_number = self.manager.session.query(Protein).count()
        self.assertEqual(29, protein_number)

    def test_protein_pathway_1(self):
        pathway = self.manager.get_pathway_by_id('path:hsa00030')
        self.assertIsNotNone(pathway)
        self.assertEqual(14, len(pathway.proteins))

    def test_protein_pathway_2(self):
        pathway = self.manager.get_pathway_by_id('path:hsa00010')
        self.assertIsNotNone(pathway)
        self.assertEqual(15, len(pathway.proteins))


