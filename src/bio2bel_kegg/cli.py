# -*- coding: utf-8 -*-

"""Command line interface."""

from bio2bel_kegg.manager import Manager

main = Manager.get_cli()

if __name__ == '__main__':
    main()
