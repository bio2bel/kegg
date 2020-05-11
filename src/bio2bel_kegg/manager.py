# -*- coding: utf-8 -*-

"""Manager for Bio2BEL KEGG."""

import logging
from typing import List, Mapping, Optional

from tqdm import tqdm

import pybel.dsl
from bio2bel.compath import CompathManager
from pybel import BELGraph
from .client import (
    ENTREZ_ID_TO_HGNC_ID, HGNC_ID_TO_SYMBOL, get_entities_lines, parse_pathway_lines,
    parse_protein_lines,
)
from .constants import KEGG, MODULE_NAME
from .models import Base, Pathway, Protein, Species, protein_pathway
from .parsers import get_entity_pathway_df, get_pathway_df

__all__ = [
    'Manager',
]

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Manager(CompathManager):
    """Protein-pathway memberships."""

    module_name = MODULE_NAME
    _base = Base
    flask_admin_models = [Pathway, Protein]
    namespace_model = pathway_model = Pathway
    edge_model = protein_pathway
    protein_model = Protein

    def get_or_create_pathway(
        self,
        kegg_pathway_id: str,
        species: Species,
        name: Optional[str] = None,
        definition: Optional[str] = None,
    ) -> Pathway:
        """Get an pathway from the database or creates it.

        :param kegg_pathway_id: A KEGG pathway identifier
        :param name: name of the pathway
        """
        if kegg_pathway_id.startswith('path:'):
            kegg_pathway_id = kegg_pathway_id[len('path:'):]

        pathway = self.get_pathway_by_id(kegg_pathway_id)
        if pathway is None:
            pathway = Pathway(
                identifier=kegg_pathway_id,
                name=name,
                definition=definition,
                species=species,
            )
            self.session.add(pathway)

        return pathway

    def get_protein_by_kegg_id(self, kegg_id: str) -> Optional[Protein]:
        """Get a protein by its kegg id.

        :param kegg_id: A KEGG identifier
        """
        return self.session.query(Protein).filter(Protein.kegg_id == kegg_id).one_or_none()

    def get_protein_by_hgnc_id(self, hgnc_id: str) -> Optional[Protein]:
        """Get a protein by its hgnc_id."""
        return self.session.query(Protein).filter(Protein.hgnc_id == hgnc_id).one_or_none()

    def get_protein_by_hgnc_symbol(self, hgnc_symbol: str) -> Optional[Protein]:
        """Get a protein by its hgnc symbol."""
        return self.session.query(Protein).filter(Protein.hgnc_symbol == hgnc_symbol).one_or_none()

    """Methods to populate the DB"""

    def _populate_pathways(self, url: Optional[str] = None):
        """Populate pathways.

        :param url: url from pathway table file
        """
        species = Species(name='Homo sapiens', taxonomy_id='9606')
        self.session.add(species)

        pathways_df = get_pathway_df(url=url)
        pathways_lines = get_entities_lines(pathways_df['kegg_pathway_id'])
        for kegg_pathway_id, pathway_lines in tqdm(pathways_lines, desc='loading pathways'):
            pathway = parse_pathway_lines(pathway_lines)
            self.get_or_create_pathway(
                kegg_pathway_id=kegg_pathway_id,
                name=pathway['name'],
                definition=pathway.get('definition'),
                species=species,
            )

        self.session.commit()

    def _pathway_protein(
        self,
        url: Optional[str] = None,
        thread_pool_size: Optional[int] = None,
    ) -> None:
        """Populate proteins.

        :param url: url from protein to pathway file
        """
        entity_pathway_df = get_entity_pathway_df(url=url)

        logger.debug('creating description URLs')
        kegg_protein_ids = list(entity_pathway_df['kegg_protein_id'].unique())

        logger.debug('protein id from index 0: %s', kegg_protein_ids[0])

        # KEGG protein ID to Protein model attributes dictionary
        logger.debug(
            'Fetching all protein meta-information. You can modify the numbers of request by modifying ThreadPool'
            ' to make this faster. However, the KEGG RESTful API might reject a big amount of requests.',
        )
        entities_lines = get_entities_lines(kegg_protein_ids, thread_pool_size=thread_pool_size)
        proteins = [
            (entity_id, parse_protein_lines(entity_lines))
            for entity_id, entity_lines in tqdm(entities_lines, desc='Parsing protein information')
        ]

        # namespace is actually kegg.genes
        kegg_protein_id_to_protein = {}
        for kegg_protein_id, protein_info in tqdm(proteins, desc='Loading proteins'):
            entrez_id = protein_info['identifier']
            hgnc_id = ENTREZ_ID_TO_HGNC_ID.get(entrez_id)
            if hgnc_id:
                hgnc_symbol = HGNC_ID_TO_SYMBOL.get(hgnc_id)
            else:
                logger.warning('no hgnc id for kegg.protein:%s', kegg_protein_id)
                hgnc_symbol = None  # FIXME can this even happen?

            kegg_protein_id_to_protein[kegg_protein_id] = protein = Protein(
                kegg_id=kegg_protein_id,
                entrez_id=entrez_id,
                hgnc_id=hgnc_id,
                hgnc_symbol=hgnc_symbol,
            )
            self.session.add(protein)

        for kegg_protein_id, kegg_pathway_id in entity_pathway_df.values:
            if kegg_pathway_id.startswith('path:'):
                kegg_pathway_id = kegg_pathway_id[len('path:'):]
            pathway = self.get_pathway_by_id(kegg_pathway_id)
            if pathway is None:
                logger.warning('could not find pathway for kegg.pathway:%s', kegg_pathway_id)
                continue
            protein = kegg_protein_id_to_protein[kegg_protein_id]
            protein.pathways.append(pathway)
        self.session.commit()

    def populate(self, pathways_url=None, protein_pathway_url=None):
        """Populate all tables."""
        self._populate_pathways(url=pathways_url)
        self._pathway_protein(url=protein_pathway_url)

    def count_pathways(self) -> int:
        """Count the pathways in the database."""
        return self._count_model(Pathway)

    def list_pathways(self) -> List[Pathway]:
        """List the pathways in the database."""
        return self._list_model(Pathway)

    def count_proteins(self) -> int:
        """Count the pathways in the database."""
        return self._count_model(Protein)

    def summarize(self) -> Mapping[str, int]:
        """Summarize the database."""
        return dict(
            pathways=self.count_pathways(),
            proteins=self.count_proteins(),
        )

    def to_bel(self) -> BELGraph:
        """Serialize KEGG to BEL."""
        graph = BELGraph(
            name='KEGG Pathway Definitions',
            version='1.0.0',
        )
        for pathway in self.list_pathways():
            pathway.add_to_bel_graph(graph)
        return graph

    def get_pathway_graph(self, kegg_id: str) -> Optional[BELGraph]:
        """Return a new graph corresponding to the pathway.

        :param kegg_id: A KEGG pathway identifier (prefixed by "path:")
        """
        pathway = self.get_pathway_by_id(kegg_id)
        if pathway is None:
            return None

        graph = BELGraph(
            name=f'Graph for kegg:{pathway.identifier} ! {pathway.name}',
        )
        pathway.add_to_bel_graph(graph)
        return graph

    def enrich_kegg_pathway(self, graph: BELGraph) -> None:
        """Enrich all proteins belonging to KEGG pathway nodes in the graph."""
        for node in list(graph):
            if isinstance(node, pybel.dsl.BiologicalProcess) and node.namespace.lower() == KEGG:
                if node.identifier:
                    pathway = self.get_pathway_by_id(node.identifier)
                else:
                    pathway = self.get_pathway_by_name(node.name)
                if pathway is None:
                    continue
                pathway.add_to_bel_graph(graph)

    def enrich_kegg_protein(self, graph: BELGraph) -> None:
        """Enrich all KEGG pathways associated with proteins in the graph."""
        for node in list(graph):
            if isinstance(node, pybel.dsl.Protein) and node.namespace.lower() == 'hgnc':
                if node.identifier:
                    protein = self.get_protein_by_hgnc_id(node.identifier)
                else:
                    protein = self.get_protein_by_hgnc_symbol(node.name)
                if protein is None:
                    continue
                for pathway in protein.pathways:
                    graph.add_part_of(node, pathway.to_pybel())

    def _add_admin(self, app, **kwargs):
        """Add admin methods."""
        from flask_admin import Admin
        from flask_admin.contrib.sqla import ModelView

        class PathwayView(ModelView):
            """Pathway view in Flask-admin."""

            column_searchable_list = (
                Pathway.identifier,
                Pathway.name,
            )

        class ProteinView(ModelView):
            """Protein view in Flask-admin."""

            column_searchable_list = (
                Protein.kegg_id,
                Protein.uniprot_id,
                Protein.hgnc_id,
                Protein.hgnc_symbol,
            )

        admin = Admin(app, **kwargs)
        admin.add_view(PathwayView(Pathway, self.session))
        admin.add_view(ProteinView(Protein, self.session))
        return admin
