Bio2BEL KEGG |build| |coverage| |documentation| |zenodo|
========================================================
This package allows the enrichment of BEL networks with KEGG information by wrapping its RESTful API.
Furthermore, it is integrated in the `ComPath environment <https://github.com/ComPath>`_ for pathway database comparison.

If you find this package useful, please consider citing [domingofernandez2018]_:

.. [domingofernandez2018] Domingo-Fernandez, D., *et al* (2018). `ComPath: an ecosystem for exploring, analyzing,
   and curating mappings across pathway databases <https://doi.org/10.1038/s41540-018-0078-8>`_.
   *Npj Systems Biology and Applications*, __5__(1), 3.

**Warning** This package creates ``partOf`` relationships in BEL, but does not convert KEGG mechanistic
relationships to BEL. That functionality is implemented in the
`PathMe project <https://github.com/pathwaymerger/pathme>`_.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bio2bel_kegg`` can be installed easily from `PyPI <https://pypi.python.org/pypi/bio2bel_kegg>`_ with the
following code in your favorite terminal:

.. code-block:: sh

    $ pip install bio2bel_kegg

or from the latest code on `GitHub <https://github.com/bio2bel/kegg>`_ in development mode with:

.. code-block:: sh

    $ git clone https://github.com/bio2bel/kegg.git
    $ cd kegg
    $ pip install -e .

Setup
-----
KEGG can be downloaded and populated from either the Python REPL or the automatically installed command line utility.

Python REPL
~~~~~~~~~~~
.. code-block:: python

    >>> import bio2bel_kegg
    >>> kegg_manager = bio2bel_kegg.Manager()
    >>> kegg_manager.populate()

Command Line Utility
~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    bio2bel_kegg populate

Other Command Line Utilities
----------------------------
- Run an admin site for simple querying and exploration :code:`python3 -m bio2bel_kegg web`
  (http://localhost:5000/admin/)
- Export gene sets for programmatic use :code:`python3 -m bio2bel_kegg export-gene-sets`

Citation
--------
- Kanehisa, Furumichi, M., Tanabe, M., Sato, Y., and Morishima, K.; KEGG: new perspectives on genomes,
  pathways, diseases and drugs. Nucleic Acids Res. 45, D353-D361 (2017).
- Kanehisa, M., Sato, Y., Kawashima, M., Furumichi, M., and Tanabe, M.; KEGG as a reference resource
  for gene and protein annotation. Nucleic Acids Res. 44, D457-D462 (2016).
- Kanehisa, M. and Goto, S.; KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Res. 28, 27-30 (2000).

.. |build| image:: https://travis-ci.org/bio2bel/kegg.svg?branch=master
    :target: https://travis-ci.org/bio2bel/kegg
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/bio2bel/kegg/coverage.svg?branch=master
    :target: https://codecov.io/gh/bio2bel/kegg?branch=master
    :alt: Coverage Status

.. |documentation| image:: http://readthedocs.org/projects/bio2bel-interpro/badge/?version=latest
    :target: http://bio2bel.readthedocs.io/projects/kegg/en/latest/?badge=latest
    :alt: Documentation Status

.. |climate| image:: https://codeclimate.com/github/bio2bel/kegg/badges/gpa.svg
    :target: https://codeclimate.com/github/bio2bel/kegg
    :alt: Code Climate

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bio2bel_kegg.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bio2bel_kegg.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bio2bel_kegg.svg
    :alt: MIT License

.. |zenodo| image:: https://zenodo.org/badge/105248163.svg
    :target: https://zenodo.org/badge/latestdoi/105248163
