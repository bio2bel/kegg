# -*- coding: utf-8 -*-

"""Kegg database model"""

from flask_admin.contrib.sqla import ModelView
from pybel.dsl import bioprocess, protein
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from bio2bel_kegg.constants import KEGG
from bio2bel_kegg.hgnc_connection import hgnc_id_to_symbol

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


class Protein(Base):
    """Genes Table"""

    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    kegg_id = Column(String(255), unique=True, nullable=False, index=True, doc='KEGG id of the protein')
    uniprot_id = Column(String(255), doc='uniprot id of the protein')
    hgnc_id = Column(String(255), doc='hgnc id of the protein')

    def __repr__(self):
        return self.id

    def serialize_to_protein_node(self):
        """Function to serialize to PyBEL node data dictionary.
        :rtype: pybel.dsl.protein
        """
        return protein(
            namespace='HGNC',
            name=str(self.get_hgnc_symbol(self.hgnc_id)),
            identifier=str(self.hgnc_id)
        )

    def get_uniprot_ids(self):
        """Returns a list of uniprot ids

        :rtype: list
        :return:
        """
        if not self.uniprot_id:
            return None

        return [
            id
            for id in self.uniprot_id.split(" ")
        ]

    def get_hgnc_symbol(self, hgnc_id):
        """Returns hgnc symbol using bio2bel_hgnc"""
        return hgnc_id_to_symbol[hgnc_id]


class PathwayView(ModelView):
    """Pathway view in Flask-admin"""
    column_searchable_list = (
        Pathway.kegg_id,
        Pathway.name
    )


class ProteinView(ModelView):
    """Protein view in Flask-admin"""
    column_searchable_list = (
        Protein.kegg_id,
        Protein.uniprot_id,
        Protein.hgnc_id
    )
