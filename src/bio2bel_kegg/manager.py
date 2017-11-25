# -*- coding: utf-8 -*-

"""
This module populates the tables of bio2bel_kegg
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from bio2bel_kegg.constants import MODULE_NAME
from bio2bel_kegg.models import Base, Pathway, Protein
from bio2bel_kegg.parsers import *

log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, connection=None):
        self.connection = get_connection(MODULE_NAME, connection)
        self.engine = create_engine(self.connection)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.session_maker()
        self.create_all()

    def create_all(self, check_first=True):
        """Create tables"""
        log.info('create table in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine)

    @staticmethod
    def ensure(connection=None):
        """Checks and allows for a Manager to be passed to the function. """
        if connection is None or isinstance(connection, str):
            return Manager(connection=connection)

        if isinstance(connection, Manager):
            return connection

        raise TypeError

    """Custom Methods to Populate the DB"""

    def get_pathway_by_id(self, kegg_id):
        """Gets a pathway by its reactome id
        :param kegg_id: kegg identifier
        :rtype: Optional[Pathway]
        """
        return self.session.query(Pathway).filter(Pathway.kegg_id == kegg_id).one_or_none()

    def _populate_pathways(self, url=None):
        """ Populate pathway table

        :param Optional[str] url: url from pathway table file
        """
        df = get_pathway_names_df(url=url)

        pathways_dict = parse_pathways(df)

        for id, name in tqdm(pathways_dict.items(), desc='Loading pathways'):
            new_pathway = Pathway(
                kegg_id=id,
                name=name,
            )

            self.session.add(new_pathway)

        self.session.commit()

    def _pathway_entity(self, url=None):
        """ Populates Protein Tables

        :param Optional[str] url: url from protein to pathway file
        """
        protein_df = get_entity_pathway_df(url=url)

        pid_protein = {}

        for protein_id, kegg_id in tqdm(parse_entity_pathway(protein_df), desc='Loading proteins'):

            if protein_id in pid_protein:
                protein = pid_protein[protein_id]
            else:
                protein = Protein(protein_id=protein_id)
                pid_protein[protein_id] = protein
                self.session.add(protein)

            pathway = self.get_pathway_by_id(kegg_id)
            protein.pathways.append(pathway)

        self.session.commit()

    def populate(self, pathways_url=None, protein_pathway_url=None):
        """ Populates all tables"""
        self._populate_pathways(url=pathways_url)
        self._pathway_entity(url=protein_pathway_url)
