Command Line Interface
======================
The command line interface allows you to communicate with the package and
perform basic functions such as:

* Populate the database: :code:`python3 -m bio2bel_kegg populate`. By default
  the database is reset every time is populated. However, another optional
  parameter "--reset-db=False", allows you to avoid the reset. More logging
  can be activated by added "-vv" or "-v" as an argument.
* Drop the database: :code:`python3 -m bio2bel_kegg drop`. More logging can
  be activated by added "-vv" or "-v" as  an rgument.
* Export gene sets as an excel file: :code:`python3 -m bio2bel_kegg export`.
