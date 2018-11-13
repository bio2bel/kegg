# -*- coding: utf-8 -*-

"""KEGG database models."""

from typing import List, Optional, Set

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import pybel.dsl
from .constants import HGNC, KEGG

Base = declarative_base()

TABLE_PREFIX = 'kegg'
PATHWAY_TABLE_NAME = f'{TABLE_PREFIX}_pathway'
PATHWAY_TABLE_HIERARCHY = f'{TABLE_PREFIX}_pathway_hierarchy'
PROTEIN_TABLE_NAME = f'{TABLE_PREFIX}_protein'
PROTEIN_PATHWAY_TABLE = f'{TABLE_PREFIX}_protein_pathway'

protein_pathway = Table(
    PROTEIN_PATHWAY_TABLE,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey(f'{PROTEIN_TABLE_NAME}.id'), primary_key=True),
    Column('pathway_id', Integer, ForeignKey(f'{PATHWAY_TABLE_NAME}.id'), primary_key=True)
)


class Pathway(Base):  # type: ignore
    """Pathway Table."""

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
        """Return name."""
        return self.name

    def __str__(self):
        """Return name."""
        return str(self.name)

    def serialize_to_pathway_node(self) -> pybel.dsl.BiologicalProcess:
        """Serialize to PyBEL node data dictionary."""
        return pybel.dsl.BiologicalProcess(
            namespace=KEGG,
            name=str(self.name),
            identifier=str(self.kegg_id)
        )

    def get_gene_set(self) -> Set['Protein']:
        """Return the genes associated with the pathway (gene set).

        Note this function restricts to HGNC symbols genes.
        """
        return {
            protein.hgnc_symbol
            for protein in self.proteins
            if protein.hgnc_symbol
        }

    @property
    def resource_id(self) -> str:
        """Return kegg identifier."""
        return self.kegg_id

    @property
    def url(self) -> str:
        """Return url pointing to kegg pathway."""
        return 'http://www.kegg.jp/dbget-bin/www_bget?pathway+map{}'.format(self.kegg_id.strip('path:hsa'))


class Protein(Base):  # type: ignore
    """Genes Table."""

    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    kegg_id = Column(String(255), nullable=False, index=True, doc='KEGG id of the protein')
    uniprot_id = Column(String(255), doc='uniprot id of the protein')
    hgnc_id = Column(String(255), doc='hgnc id of the protein')
    hgnc_symbol = Column(String(255), doc='hgnc symbol of the protein')

    def __repr__(self):
        """Return HGNC symbol."""
        return str(self.hgnc_symbol)

    def __str__(self):
        """Return HGNC symbol."""
        return str(self.hgnc_symbol)

    def to_pybel(self) -> pybel.dsl.Protein:
        """Serialize to PyBEL node data dictionary."""
        return pybel.dsl.Protein(
            namespace=HGNC,
            name=self.hgnc_symbol,
            identifier=str(self.hgnc_id)
        )

    def get_uniprot_ids(self) -> Optional[List[str]]:
        """Return a list of uniprot ids."""
        if not self.uniprot_id:
            return None

        return self.uniprot_id.split(" ")

    def get_pathways_ids(self) -> Set[str]:
        """Return the pathways associated with the protein."""
        return {
            pathway.kegg_id
            for pathway in self.pathways
        }
