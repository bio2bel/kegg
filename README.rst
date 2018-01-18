Bio2BEL KEGG |build| |coverage| |docs|
======================================
This package converts KEGG to BEL. So far, exporting the pathway namespace has been implemented.

Installation
------------
This code can be installed with :code:`pip3 install git+https://github.com/bio2bel/kegg.git`

Creating a Local Copy of the Namespace
--------------------------------------
A BEL namespace can be generated with :code:`python3 -m bio2bel_kegg write -o ~/Downloads/kegg.belns`

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
