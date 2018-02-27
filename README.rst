Bio2BEL KEGG |build| |coverage| |docs|
======================================
This package allows the enrichment of BEL networks with KEGG information by wrapping its RESTful API.
Furthermore, it is integrated in the `ComPath environment <https://github.com/ComPath>`_ for pathway database comparison.

Installation
------------
This code can be installed with :code:`pip3 install git+https://github.com/bio2bel/kegg.git`

Functionalities and Commands
----------------------------
Following, the main functionalities and commands to work with this package:

- Populate local database with KEGG info :code:`python3 -m bio2bel_kegg populate`
- Run an admin site for simple querying and exploration :code:`python3 -m bio2bel_kegg web` (http://localhost:5000/admin/)
- Export gene sets for programmatic use :code:`python3 -m bio2bel_kegg export`

Citation
--------
- Kanehisa, Furumichi, M., Tanabe, M., Sato, Y., and Morishima, K.; KEGG: new perspectives on genomes, pathways, diseases and drugs. Nucleic Acids Res. 45, D353-D361 (2017).
- Kanehisa, M., Sato, Y., Kawashima, M., Furumichi, M., and Tanabe, M.; KEGG as a reference resource for gene and protein annotation. Nucleic Acids Res. 44, D457-D462 (2016).
- Kanehisa, M. and Goto, S.; KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Res. 28, 27-30 (2000).


.. |build| image:: https://travis-ci.org/bio2bel/kegg.svg?branch=master
    :target: https://travis-ci.org/bio2bel/kegg
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/kegg/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/kegg?branch=master
    :alt: Coverage Status

.. |docs| image:: http://readthedocs.org/projects/bio2bel-kegg/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/kegg/en/latest/?badge=latest
    :alt: Documentation Status
