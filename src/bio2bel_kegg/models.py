# -*- coding: utf-8 -*-

"""KEGG database models."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import pybel.dsl
from bio2bel.compath import CompathPathwayMixin, CompathProteinMixin
from bio2bel.manager.models import SpeciesMixin
from .constants import HGNC, KEGG, MODULE_NAME

Base = declarative_base()

SPECIES_TABLE_NAME = f'{MODULE_NAME}_species'
PATHWAY_TABLE_NAME = f'{MODULE_NAME}_pathway'
PATHWAY_TABLE_HIERARCHY = f'{MODULE_NAME}_pathway_hierarchy'
PROTEIN_TABLE_NAME = f'{MODULE_NAME}_protein'
PROTEIN_PATHWAY_TABLE = f'{MODULE_NAME}_protein_pathway'

protein_pathway = Table(
    PROTEIN_PATHWAY_TABLE,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey(f'{PROTEIN_TABLE_NAME}.id'), primary_key=True),
    Column('pathway_id', Integer, ForeignKey(f'{PATHWAY_TABLE_NAME}.id'), primary_key=True),
)


class Species(Base, SpeciesMixin):
    """Species table."""

    __tablename__ = SPECIES_TABLE_NAME


class Pathway(Base, CompathPathwayMixin):
    """Pathway Table."""

    __tablename__ = PATHWAY_TABLE_NAME
    id = Column(Integer, primary_key=True)  # noqa:A003

    bel_encoding = 'B'
    prefix = KEGG
    identifier = Column(String(255), unique=True, nullable=False, index=True, doc='KEGG id of the pathway')
    name = Column(String(255), nullable=False, doc='pathway name')
    definition = Column(Text, nullable=True, doc='pathway description')

    species = relationship(Species, backref='pathways')
    species_id = Column(Integer, ForeignKey(f'{Species.__tablename__}.id'))

    proteins = relationship(
        'Protein',
        secondary=protein_pathway,
        backref='pathways',
    )


class Protein(Base, CompathProteinMixin):
    """Genes Table."""

    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)  # noqa:A003

    kegg_id = Column(String(255), nullable=False, index=True, doc='KEGG id of the protein')
    entrez_id = Column(String(255), nullable=False, index=True, doc='Entrez identifier')
    uniprot_id = Column(String(255), doc='uniprot id of the protein (there could be more than one)')
    hgnc_id = Column(String(255), doc='hgnc id of the protein')
    hgnc_symbol = Column(String(255), doc='hgnc symbol of the protein')

    def __repr__(self):
        """Return HGNC symbol."""
        return f'Protein(kegg_id={self.kegg_id}, ' \
               f'uniprot_id={self.uniprot_id}, hgnc_id={self.hgnc_id}, hgnc_symbol={self.hgnc_symbol})'

    def __str__(self):
        """Return HGNC symbol."""
        return str(self.hgnc_symbol)

    def to_pybel(self) -> pybel.dsl.Protein:
        """Serialize to PyBEL node data dictionary."""
        return pybel.dsl.Protein(
            namespace=HGNC,
            identifier=self.hgnc_id,
            name=self.hgnc_symbol,
        )

    def get_uniprot_ids(self) -> Optional[List[str]]:
        """Return a list of uniprot ids."""
        if not self.uniprot_id:
            return None

        return self.uniprot_id.split(" ")
