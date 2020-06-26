# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_indexer.api import RecordIndexer
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, check_elasticsearch

from cuor.organizations.pidstore import ORGANIZATION_PID_TYPE, ORGANIZATION_PID_MINTER, ORGANIZATION_PID_FETCHER
from cuor.organizations.search import OrganizationSearch
from cuor.organizations.api import OrganizationRecord


def _(x):
    """Identity function for string extraction."""
    return x


RECORDS_REST_ENDPOINTS = {
    'recid': dict(
        pid_type=ORGANIZATION_PID_TYPE,
        pid_minter=ORGANIZATION_PID_MINTER,
        pid_fetcher=ORGANIZATION_PID_FETCHER,
        default_endpoint_prefix=True,
        record_class=OrganizationRecord,
        search_class=OrganizationSearch,
        indexer_class=RecordIndexer,
        search_index='organizations',
        search_type=None,
        record_serializers={
            'application/json': ('cuor.organizations.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('cuor.organizations.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('cuor.organizations.loaders'
                                 ':json_v1'),
        },
        list_route='/organizations/',
        item_route='/organizations/<pid(recid,'
                   'record_class="cuor.organizations.api.OrganizationRecord")'
                   ':pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
        list_permission_factory_imp=allow_all,
        links_factory_imp='invenio_records_files.'
                          'links:default_record_files_links_factory',
    ),
}


"""REST API for cuor."""

RECORDS_UI_ENDPOINTS = dict(
    recid=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>',
        template='organizations/organization.html',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),
    recid_previewer=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>/preview/<path:filename>',
        view_imp='invenio_previewer.views.preview',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),
    recid_files=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>/files/<path:filename>',
        view_imp='invenio_records_files.utils.file_download_ui',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),
)
"""Records UI for cuor."""

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/organizations/results.html'
"""Result list template."""

PIDSTORE_RECID_FIELD = 'id'

CUOR_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""


RECORDS_REST_FACETS = dict(
    organizations=dict(
        aggs=dict(
            type=dict(terms=dict(field='type')),
            keywords=dict(terms=dict(field='keywords'))
        ),
        post_filters=dict(
            type=terms_filter('type'),
            keywords=terms_filter('keywords'),
        )
    )
)
"""Introduce searching facets."""


RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=2,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query='bestmatch',
        noquery='mostrecent',
    )
)
"""Set default sorting options."""

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'recid': '/files'
    },
}
"""Records files integration."""

FILES_REST_PERMISSION_FACTORY = \
    'cuor.organizations.permissions:files_permission_factory'
"""Files-REST permissions factory."""
