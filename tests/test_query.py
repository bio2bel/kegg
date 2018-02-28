# -*- coding: utf-8 -*-
""" This module contains tests for parsing KEGG files"""

from tests.constants import DatabaseMixin


class TestQuery(DatabaseMixin):
    """Tests Manager query methods"""

    def test_gene_query_1(self):
        """Single protein query. This protein is associated with 3 pathways"""
        enriched_pathways = self.manager.query_gene_set(['PFKP'])
        self.assertIsNotNone(enriched_pathways, msg='Enriching function is not working')

        self.assertEqual(
            {
                'path:hsa00010': [1, 16],
                'path:hsa00030': [1, 14],
            },
            enriched_pathways
        )
