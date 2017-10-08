# -*- coding: utf-8 -*-

"""Kegg database model"""

from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pybel.constants import FUNCTION, NAMESPACE, NAME, BIOPROCESS

Base = declarative_base()

TABLE_PREFIX = 'kegg'
PATHWAY_TABLE_NAME = '{}_pathway'.format(TABLE_PREFIX)
PATHWAY_TABLE_HIERARCHY = '{}_pathway_hierarchy'.format(TABLE_PREFIX)
UNIPROT_TABLE_NAME = '{}_uniprot'.format(TABLE_PREFIX)
UNIPROT_PATHWAY_TABLE = '{}_uniprot_pathway'.format(TABLE_PREFIX)

uniprot_pathway = Table(
    UNIPROT_PATHWAY_TABLE,
    Base.metadata,
    Column('uniprot_id', Integer, ForeignKey('{}.id'.format(UNIPROT_TABLE_NAME))),
    Column('pathway_id', Integer, ForeignKey('{}.kegg_id'.format(PATHWAY_TABLE_NAME)))
)


class Pathway(Base):
    """Pathway Table"""

    __tablename__ = PATHWAY_TABLE_NAME

    kegg_id = Column(String(255), primary_key=True)

    name = Column(String(255))

    genes = relationship(
        'UniProt',
        secondary=uniprot_pathway,
        backref='pathways'
    )

    def __repr__(self):
        return self.name

    def serialize_to_pathway_node(self):
        """Function to serialize to PyBEL node data dictionary.
        :rtype: dict
        """
        return {
            FUNCTION: BIOPROCESS,
            NAMESPACE: 'KEGG',
            NAME: self.name
        }


class UniProt(Base):
    """Genes Table"""

    __tablename__ = UNIPROT_TABLE_NAME

    id = Column(String(255), primary_key=True)

    def __repr__(self):
        return self.id
