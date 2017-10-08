# -*- coding: utf-8 -*-

"""
This module populates the tables of bio2bel_kegg
"""

import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bio2bel_kegg.constants import *
from src.bio2bel_kegg.parsers.pathways import parser_pathways
from src.bio2bel_kegg.parsers.entities import parser_entity
from src.bio2bel_kegg.models import Base, Pathway, UniProt
from src.bio2bel_kegg.run import get_data

import logging

log = logging.getLogger(__name__)


class Manager(object):
    def __init__(self, connection=None):
        self.connection = self.get_connection(connection)
        self.engine = create_engine(self.connection)
        self.sessionmake = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = self.sessionmake()
        self.drop_tables()  # TODO: delete?
        self.make_tables()

    @staticmethod
    def get_connection(connection=None):
        """Return the SQLAlchemy connection string if it is set
        :param connection: get the SQLAlchemy connection string
        :rtype: str
        """
        if connection:
            return connection

        config = configparser.ConfigParser()

        cfp = KEGG_CONFIG_FILE_PATH

        if os.path.exists(cfp):
            log.info('fetch database configuration from {}'.format(cfp))
            config.read(cfp)
            connection = config['database']['sqlalchemy_connection_string']
            log.info('load connection string from {}: {}'.format(cfp, connection))
            return connection

        with open(cfp, 'w') as config_file:
            config['database'] = {'sqlalchemy_connection_string': KEGG_SQLITE_PATH}
            config.write(config_file)
            log.info('create configuration file {}'.format(cfp))

        return KEGG_SQLITE_PATH

    def make_tables(self, check_first=True):
        """Create tables"""
        log.info('create table in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_tables(self):
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

    def _populate_pathways(self, source=None):
        """ Populate pathway table

        :param source: path or link to data source needed for get_data()
        """

        if source is None:
            source = KEGG_PATHWAYS_URL

        df = get_data(source)

        pathways_dict = parser_pathways(df)

        for id, name in pathways_dict.items():
            new_pathway = Pathway(
                kegg_id=id,
                name=name,
            )

            self.session.add(new_pathway)

        self.session.commit()

    def _pathway_entity(self, uniprot_url=None):
        """ Populates UniProt Tables"""

        if uniprot_url is None:
            uniprot_url = KEGG_GENE_MAPPING_URL

        uniprot_df = get_data(uniprot_url)

        uniprots = parser_entity(uniprot_df)

        for uniprot_id, reactome_id, evidence in uniprots:
            pathway = self.session.query(Pathway).get(reactome_id)

            uniprot = UniProt(
                id=uniprot_id,
                pathways=pathway
            )

            self.session.add(uniprot)

    def populate(self):
        """ Populates all tables"""
        self._populate_pathways()
