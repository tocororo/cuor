# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_records_rest.facets import terms_filter


def _(x):
    """Identity function for string extraction."""
    return x


PIDSTORE_RECID_FIELD = 'id'

CUOR_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""


RECORDS_REST_FACETS = dict(
    organizations=dict(
        filters=dict(
            status=terms_filter('status'),
            types=terms_filter('types'),
            country=terms_filter('addresses.country'),
            state=terms_filter('addresses.state'),
        ),
        aggs=dict(
            status=dict(
                terms=dict(
                    field='status',
                    size=5
                )
            ),
            types=dict(
                terms=dict(
                    field='types',
                    size=8
                )
            ),
            country=dict(
                terms=dict(
                    field='addresses.country',
                    size=8
                )
            ),
            state = dict(
                terms=dict(
                    field='addresses.state',
                    size=5
                )
            )
        )
    )
)
"""Introduce searching facets."""


# TODO: see how implement better sort
RECORDS_REST_SORT_OPTIONS = dict(
    organizations=dict(
        # mostrecent=dict(
        #     title=_('Most recent'),
        #     fields=['-_created'],
        #     default_order='asc',
        #     order=1,
        # ),
        bestmatch=dict(
                title=_('Best match'),
                fields=['_score'],
                default_order='desc',
                order=1,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    organizations=dict(
        query='bestmatch',
        noquery='bestmatch',
    )
)
"""Set default sorting options."""

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'orgid': '/files'
    },
}
"""Records files integration."""

FILES_REST_PERMISSION_FACTORY = \
    'cuor.organizations.permissions:files_permission_factory'
"""Files-REST permissions factory."""
