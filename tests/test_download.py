# -*- coding: utf-8 -*-

"""Test parsing of descriptions."""

import unittest

from bio2bel_kegg.client import parse_pathway_lines, parse_protein_lines
from tests.constants import test_pathway_path, test_protein_path


class TestDescriptionParse(unittest.TestCase):
    """Test parsing of description."""

    def test_pathway_parser(self):
        """Test the pathway parser."""
        with open(test_pathway_path) as file:
            parse_pathway_lines(file)

    def test_protein_parser(self):
        """Test the protein parser."""
        with open(test_protein_path) as file:
            parse_protein_lines(file)

    # def test_description_protein(self):
    #     """Test parsing description of a protein."""
    #     response = requests.get('http://rest.kegg.jp/get/hsa:5214')
    #
    #     pfkp_protein = parse_description(response.text.split('\n'))
    #
    #     self.assertEqual(
    #         [
    #             ('hsa00010', 'Glycolysis / Gluconeogenesis'),
    #             ('hsa00030', 'Pentose phosphate pathway'),
    #             ('hsa00051', 'Fructose and mannose metabolism'),
    #             ('hsa00052', 'Galactose metabolism'),
    #             ('hsa01100', 'Metabolic pathways'),
    #             ('hsa01200', 'Carbon metabolism'),
    #             ('hsa01230', 'Biosynthesis of amino acids'),
    #             ('hsa03018', 'RNA degradation'),
    #             ('hsa04152', 'AMPK signaling pathway'),
    #             ('hsa04919', 'Thyroid hormone signaling pathway'),
    #             ('hsa05230', 'Central carbon metabolism in cancer')
    #         ],
    #         pfkp_protein['PATHWAY']
    #     )
    #
    #     self.assertEqual(
    #         [
    #             ('NCBI-GeneID', '5214'),
    #             ('NCBI-ProteinID', 'NP_002618'),
    #             ('OMIM', '171840'),
    #             ('HGNC', '8878'),
    #             ('Ensembl', 'ENSG00000067057'),
    #             ('Vega', 'OTTHUMG00000017556'),
    #             ('Pharos', 'Q01813(Tbio)'),
    #             ('UniProt', 'Q01813'),
    #         ],
    #         pfkp_protein[DBLINKS]
    #     )
    #
    #     description_links = get_description_properties(pfkp_protein, DBLINKS, PROTEIN_RESOURCES)
    #
    #     self.assertDictEqual(
    #         {
    #             'HGNC': '8878',
    #             'UniProt': 'Q01813'
    #         },
    #         description_links
    #     )
