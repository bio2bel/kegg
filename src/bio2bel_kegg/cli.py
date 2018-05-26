# -*- coding: utf-8 -*-


import logging

from bio2bel_kegg.manager import Manager

log = logging.getLogger(__name__)

main = Manager.get_cli()

if __name__ == '__main__':
    main()
