# -*- coding: utf-8 -*-

"""Bio2BEL KEGG is a package to build KEGG gene sets in the ComPath environment.

Bio2BEL KEGG is a package for enriching BEL networks with KEGG information by wrapping its RESTful API.
KEGG. This package downloads pathway information from KEGG's API and store it in template data model relating genes
to pathways. Furthermore, it is integrated in the `ComPath environment <https://github.com/ComPath>`_ for pathway
database comparison.

Citation
--------
- Kanehisa, Furumichi, M., Tanabe, M., Sato, Y., and Morishima, K.; KEGG: new perspectives on genomes, pathways,
  diseases and drugs. Nucleic Acids Res. 45, D353-D361 (2017).
- Kanehisa, M., Sato, Y., Kawashima, M., Furumichi, M., and Tanabe, M.; KEGG as a reference resource for gene and
  protein annotation. Nucleic Acids Res. 44, D457-D462 (2016).
- Kanehisa, M. and Goto, S.; KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Res. 28, 27-30 (2000).
"""

from .manager import Manager  # noqa: F401
