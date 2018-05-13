# -*- coding: utf-8 -*-

"""KEGG database models"""

from pybel.dsl import bioprocess, protein
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .constants import KEGG, HGNC

Base = declarative_base()

TABLE_PREFIX = 'kegg'
PATHWAY_TABLE_NAME = '{}_pathway'.format(TABLE_PREFIX)
PATHWAY_TABLE_HIERARCHY = '{}_pathway_hierarchy'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
PROTEIN_PATHWAY_TABLE = '{}_protein_pathway'.format(TABLE_PREFIX)

protein_pathway = Table(
    PROTEIN_PATHWAY_TABLE,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
    Column('pathway_id', Integer, ForeignKey('{}.id'.format(PATHWAY_TABLE_NAME)), primary_key=True)
)


class Pathway(Base):
    """Pathway Table"""

    __tablename__ = PATHWAY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    kegg_id = Column(String(255), unique=True, nullable=False, index=True, doc='KEGG id of the pathway')
    name = Column(String(255), doc='pathway name')

    proteins = relationship(
        'Protein',
        secondary=protein_pathway,
        backref='pathways'
    )

    def __repr__(self):
        return self.name

    def serialize_to_pathway_node(self):
        """Function to serialize to PyBEL node data dictionary.
        :rtype: pybel.dsl.bioprocess
        """
        return bioprocess(
            namespace=KEGG,
            name=str(self.name),
            identifier=str(self.kegg_id)
        )

    def get_gene_set(self):
        """Return the genes associated with the pathway (gene set). Note this function restricts to HGNC symbols genes.

        :rtype: set[bio2bel_kegg.models.Protein]
        """
        return {
            protein.hgnc_symbol
            for protein in self.proteins
            if protein.hgnc_symbol
        }

    @property
    def resource_id(self):
        return self.kegg_id

    @property
    def url(self):
        return 'http://www.kegg.jp/dbget-bin/www_bget?pathway+map{}'.format(self.kegg_id.strip('path:hsa'))


class Protein(Base):
    """Genes Table"""

    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    kegg_id = Column(String(255), nullable=False, index=True, doc='KEGG id of the protein')
    uniprot_id = Column(String(255), doc='uniprot id of the protein')
    hgnc_id = Column(String(255), doc='hgnc id of the protein')
    hgnc_symbol = Column(String(255), doc='hgnc symbol of the protein')

    def __repr__(self):
        return self.hgnc_id

    def serialize_to_protein_node(self):
        """Function to serialize to PyBEL node data dictionary.
        :rtype: pybel.dsl.protein
        """
        return protein(
            namespace=HGNC,
            name=self.hgnc_symbol,
            identifier=str(self.hgnc_id)
        )

    def get_uniprot_ids(self):
        """Return a list of uniprot ids.

        :rtype: list
        :return:
        """
        if not self.uniprot_id:
            return None

        return [
            id
            for id in self.uniprot_id.split(" ")
        ]

    def get_pathways_ids(self):
        """Return the pathways associated with the protein."""
        return {
            pathway.kegg_id
            for pathway in self.pathways
        }
