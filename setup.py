# -*- coding: utf-8 -*-

"""Setup module for Bio2BEL KEGG."""

import codecs
import os
import re

import setuptools

BIO2BEL_MODULE = 'kegg'
PACKAGES = setuptools.find_packages(where='src')
META_PATH = os.path.join('src', f'bio2bel_{BIO2BEL_MODULE}', '__init__.py')
KEYWORDS = ['Biological Expression Language', 'BEL', 'KEGG', 'Systems Biology', 'Networks Biology']
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
]
INSTALL_REQUIRES = [
    'click==7.0',
    'requests==2.22.0',
    'bio2bel>=0.2.1',
    'pybel==0.14.1',
    'sqlalchemy==1.3.8',
    'pandas==0.24.2',
    'compath_utils>=0.2.1',
    'bio2bel_hgnc>=0.2.3',
    'bel_resources==0.0.3',
    'tqdm==4.31.1',
    'flask==1.1.1',
    'flask_admin==1.5.3',
]
EXTRAS_REQUIRE = {
    'web': [
        'flask',
        'flask_admin',
    ],
    'docs': [
        'sphinx',
        'sphinx-rtd-theme',
        'sphinx-click',
    ],
}
ENTRY_POINTS = {
    'bio2bel': [
        f'{BIO2BEL_MODULE} = bio2bel_{BIO2BEL_MODULE}',
    ],
    'compath': [
        f'{BIO2BEL_MODULE} = bio2bel_{BIO2BEL_MODULE}'
    ],
    'console_scripts': [
        f'bio2bel_{BIO2BEL_MODULE} = bio2bel_{BIO2BEL_MODULE}.cli:main',
    ]
}

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Build an absolute path from *parts* and return the contents of the resulting file. Assume UTF-8 encoding."""
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """Extract __*meta*__ from META_FILE."""
    meta_match = re.search(
        r'^__{meta}__ = ["\']([^"\']*)["\']'.format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string'.format(meta=meta))


def get_long_description():
    """Get the long_description from the README.rst file. Assume UTF-8 encoding."""
    with codecs.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


if __name__ == '__main__':
    setuptools.setup(
        name=find_meta('title'),
        version=find_meta('version'),
        description=find_meta('description'),
        long_description=get_long_description(),
        url=find_meta('url'),
        author=find_meta('author'),
        author_email=find_meta('email'),
        maintainer=find_meta('author'),
        maintainer_email=find_meta('email'),
        license=find_meta('license'),
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        package_dir={'': 'src'},
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        entry_points=ENTRY_POINTS,
        zip_safe=False,
    )
