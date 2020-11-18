# -*- coding: utf-8 -*-

"""This module parsers the description files -> http://rest.kegg.jp/get/ in KEGG RESTful API."""

import itertools as itt
import logging
import os
from multiprocessing.pool import ThreadPool
from operator import itemgetter
from typing import Any, Collection, Iterable, List, Mapping, Optional, Tuple
from urllib.request import urlretrieve

from protmapper.api import hgnc_name_to_id
from protmapper.uniprot_client import get_entrez_id, um
from tqdm import tqdm

from .constants import ENTITY_DIRECTORY, XREF_MAPPING

__all__ = [
    'get_entities_lines',
    'parse_protein_lines',
    'parse_pathway_lines',
]

logger = logging.getLogger(__name__)

HGNC_ID_TO_ENTREZ_ID = {
    hgnc: get_entrez_id(uniprot)
    for uniprot, hgnc in um.uniprot_hgnc.items()
}
ENTREZ_ID_TO_HGNC_ID = {v: k for k, v in HGNC_ID_TO_ENTREZ_ID.items()}
HGNC_ID_TO_SYMBOL = {v: k for k, v in hgnc_name_to_id.items()}


def get_entities_lines(
    entity_ids: Collection[str],
    thread_pool_size: Optional[int] = None,
) -> List[Tuple[str, List[str]]]:
    """Get entities.

    :param entity_ids: Can be KEGG pathway identifiers or KEGG protein identifiers
    :param thread_pool_size:
    """
    # Multi-thread processing of protein description requests
    if thread_pool_size is None:
        thread_pool_size = 3
    with ThreadPool(processes=thread_pool_size) as pool:
        results: Iterable[Tuple[str, List[str]]] = pool.imap_unordered(ensure_kegg_entity, entity_ids)
        # make sure it gets the whole way through this before doing the next step
        results: Iterable[Tuple[str, List[str]]] = tqdm(
            results,
            total=len(entity_ids),
            desc=f'Fetching protein information ({thread_pool_size} threads)',
        )
        return list(results)


def ensure_kegg_entity(entity_id: str) -> Tuple[str, List[str]]:
    """Send a given entity to the KEGG API and process the results.

    :param entity_id: A KEGG entity identifier (with prefix)
    """
    prefix, identifier = entity_id.split(':', 1)
    entity_type_directory = os.path.join(ENTITY_DIRECTORY, prefix)
    os.makedirs(entity_type_directory, exist_ok=True)
    entity_text_path = os.path.join(entity_type_directory, f'{identifier}.txt')

    if not os.path.exists(entity_text_path):
        urlretrieve(f'http://rest.kegg.jp/get/{entity_id}', entity_text_path)  # noqa:S310

    with open(entity_text_path) as file:
        lines = [line.strip() for line in file]

    return entity_id, lines


def iterate_groups(lines):
    current_key = None
    current_subkey = None
    for line in lines:
        if line.startswith('///') or not line.strip():
            continue
        key, val = line[:12].rstrip(), line[12:].rstrip()
        if key:
            if not key.startswith(' '):
                current_key = key
                current_subkey = None
            else:
                current_subkey = key.strip()

        if current_subkey is not None:
            yield (current_key, current_subkey), val
        else:
            yield current_key, val


def get_line(lines: Iterable[str]) -> str:
    return list(lines)[0]


def parse_protein_lines(lines: Iterable[str]) -> Mapping[str, Any]:
    """Parse the lines of a KEGG protein info file."""
    rv = {'xrefs': []}
    for group, group_lines in itt.groupby(iterate_groups(lines), key=itemgetter(0)):
        group_lines = (line for _, line in group_lines)
        if group == 'ENTRY':
            line = get_line(group_lines)
            kegg_id, _, _ = [x.strip() for x in line.split() if x.strip()]  # not sure what the other two are
            rv['identifier'] = kegg_id.strip()
        elif group == 'DEFINITION':
            rv['definition'] = get_line(group_lines)
        elif group == 'ORTHOLOGY':
            rv['orthology'] = _get_xref_names(group_lines, prefix='kegg.orthology')
        elif group == 'ORGANISM':
            line: str = get_line(group_lines)
            p_index = line.index('(')
            rv['species'] = {'name': line[:p_index].rstrip()}
        elif group == 'PATHWAY':
            rv['pathway'] = _get_xref_names(group_lines, prefix='kegg.pathway')
        elif group == 'BRITE':
            pass
        elif group == 'POSITION':
            pass  # rv['position'] = int(get_line(lines))
        elif group == 'MOTIF':
            rv['motif'] = _get_xrefs(group_lines)
        elif group == 'DBLINKS':
            rv['xrefs'] = _get_xrefs(group_lines)
        else:
            pass  # logger.warning(f'unhandled group: {group}')
    return rv


def parse_pathway_lines(lines: Iterable[str]) -> Mapping[str, Any]:
    """Parse the lines of a KEGG pathway info file."""
    rv = {}
    for group, group_lines in itt.groupby(iterate_groups(lines), key=itemgetter(0)):
        group_lines = (line for _, line in group_lines)
        if group == 'ENTRY':
            line = get_line(group_lines)
            kegg_id, _ = line.split()
            rv['identifier'] = kegg_id
        elif group == 'NAME':
            rv['name'] = get_line(group_lines)
        elif group == 'DESCRIPTION':
            rv['definition'] = get_line(group_lines)
        elif group == 'CLASS':
            pass
        elif group == 'PATHWAY_MAP':
            pass
        elif group == 'MODULE':
            pass
        elif group == 'NETWORK':
            pass
        elif group == 'DRUG':
            drugs = []
            for line in group_lines:
                xref, name = line.split('  ')
                try:
                    p_index = name.rindex('(')
                except ValueError:
                    logger.warning(f'could not parse line: {line}')
                    continue
                name, note = name[:p_index - 1], name[1 + p_index:].rstrip().rstrip(')')
                drugs.append({'identifier': xref, 'name': name, 'note': note.split('/')})
            rv['drugs'] = drugs
        elif group == 'DISEASE':
            rv['diseases'] = _get_xref_names(group_lines, prefix='kegg.disease')
        elif group == 'DBLINKS':
            rv['xrefs'] = _get_xrefs(group_lines)
        elif group == 'ORGANISM':
            line: str = get_line(group_lines)
            p_index = line.index('(')
            rv['species'] = {'name': line[:p_index].rstrip()}
        elif group == 'GENE':
            genes = []
            for line in group_lines:
                xref, info = line.split('  ', 1)
                symbol, info = info.split(';')
                name, info = info.lstrip().split(' [', 1)
                orthology, ec = info.split(']', 1)
                orthology_codes = orthology[len('KO:'):].split(' ')

                if ec.strip().lstrip('[').rstrip(']'):
                    ec_codes = ec[len('EC:'):].split(' ')
                else:
                    ec_codes = []

                genes.append({
                    'prefix': 'ncbigene',
                    'identifier': xref,
                    'name': symbol,
                    'definition': name,
                    'orthologies': [
                        {
                            'prefix': 'kegg.orthology',
                            'identifier': orthology_code,
                        }
                        for orthology_code in orthology_codes
                    ],
                    'enzyme_classes': [
                        {'prefix': 'ec-code', 'identifier': ec_code}
                        for ec_code in ec_codes
                    ],
                })
            rv['genes'] = genes
        elif group == 'COMPOUND':
            rv['compounds'] = _get_xref_names(group_lines, prefix='kegg.compound')
        elif group == 'REFERENCE':
            line = get_line(group_lines)
            if line.startswith('PMID'):
                pubmed_id = line[len('PMID:'):]
                rv['reference'] = {'pubmed_id': pubmed_id}
            else:
                continue
        elif group == 'REL_PATHWAY':
            rv['related'] = _get_xref_names(group_lines, prefix='kegg.pathway')
        elif group == 'KO_PATHWAY':
            pass
        else:
            pass  # logger.warning(f'unhandled group: {group}')

    return rv


def _get_xrefs(group_lines: Iterable[str]) -> List[Mapping[str, Any]]:
    xrefs_list = []
    for line in group_lines:
        prefix, xrefs = line.strip().split(':')
        prefix = XREF_MAPPING.get(prefix, prefix)
        for xref in xrefs.strip().split(' '):
            xrefs_list.append({'prefix': prefix, 'identifier': xref})
    return xrefs_list


def _get_xref_names(group_lines, prefix):
    rv = []
    for line in group_lines:
        try:
            xref, name = line.split('  ')
        except ValueError:
            logger.warning(f'Could not split line: {line}')
            continue
        rv.append({'prefix': prefix, 'identifier': xref, 'name': name})
    return rv
