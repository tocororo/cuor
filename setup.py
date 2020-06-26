# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Cuban Organizations Registry"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('cuor', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='cuor',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='cuor Invenio',
    license='MIT',
    author='SCEIBA Project',
    author_email='eduardo.arencibia@upr.edu.cu',
    url='https://github.com/tocororo/cuor',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'cuor = invenio_app.cli:cli',
        ],
        'invenio_base.apps': [
            'cuor_records = cuor.organizations:CuOrgRegistry',
            'cuor_harvester = cuor.harvester.ext:CuORHarvester',
        ],
        'invenio_base.blueprints': [
            'cuor = cuor.theme.views:blueprint',
            'cuor_records = cuor.organizations.views:blueprint',
        ],
        'invenio_assets.webpack': [
            'cuor_theme = cuor.theme.webpack:theme',
        ],
        'invenio_config.module': [
            'cuor = cuor.config',
        ],
        'invenio_i18n.translations': [
            'messages = cuor',
        ],
        'invenio_base.api_apps': [
            'cuor = cuor.organizations:CuOrgRegistry',
         ],
        'invenio_jsonschemas.schemas': [
            'cuor = cuor.organizations.jsonschemas'
        ],
        'invenio_search.mappings': [
            'organizations = cuor.organizations.mappings'
        ],
        'invenio_pidstore.fetchers': [
            'recids = cuor.organizations.pidstore:identifiers_fetcher',
            'orgid = cuor.organizations.pidstore:organization_uuid_fetcher',
        ],
        'invenio_pidstore.minters': [
            'recids = cuor.organizations.pidstore:identifiers_minter',
            'orgid = cuor.organizations.pidstore:organization_uuid_minter',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
