# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# Cuban Organizations Registry is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Default configuration for Cuban Organizations Registry.

You overwrite and set instance-specific configuration by either:

- Configuration file: ``<virtualenv prefix>/var/instance/invenio.cfg``
- Environment variables: ``APP_<variable name>``
"""

from __future__ import absolute_import, print_function

from datetime import timedelta

from invenio_app.config import APP_DEFAULT_SECURE_HEADERS
from invenio_previewer.config import PREVIEWER_PREFERENCE as BASE_PREFERENCE
from cuor.configvariables import *
import os

from cuor.organizations.pidstore import ORGANIZATION_TYPE, ORGANIZATION_PID_TYPE, ORGANIZATION_PID_MINTER, ORGANIZATION_PID_FETCHER
from cuor.organizations.search import OrganizationSearch
from cuor.organizations.api import OrganizationRecord
from invenio_indexer.api import RecordIndexer
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, check_elasticsearch


def _(x):
    """Identity function used to trigger string extraction."""
    return x


# Rate limiting
# =============
#: Storage for ratelimiter.
RATELIMIT_STORAGE_URL = 'redis://' + IP_REDIS + ':6379/3'

# I18N
# ====
#: Default language
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default time zone
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages (do not include the default language in list).
I18N_LANGUAGES = [
    # ('fr', _('French'))
]

# Base templates
# ==============
#: Global base template.
BASE_TEMPLATE = 'cuor/page.html'
#: Cover page base template (used for e.g. login/sign-up).
COVER_TEMPLATE = 'invenio_theme/page_cover.html'
#: Footer base template.
FOOTER_TEMPLATE = 'invenio_theme/footer.html'
#: Header base template.
HEADER_TEMPLATE = 'invenio_theme/header.html'
#: Settings base template.
SETTINGS_TEMPLATE = 'invenio_theme/page_settings.html'

# Theme configuration
# ===================
#: Site name
THEME_SITENAME = _('Cuban Organizations Registry')
#: Use default frontpage.
THEME_FRONTPAGE = True
#: Frontpage title.
THEME_FRONTPAGE_TITLE = _('Cuban Organizations Registry')
#: Frontpage template.
THEME_FRONTPAGE_TEMPLATE = 'cuor/frontpage.html'

# Email configuration
# ===================
#: Email address for support.
SUPPORT_EMAIL = "eduardo.arencibia@upr.edu.cu"
#: Disable email sending by default.
MAIL_SUPPRESS_SEND = True

# Assets
# ======
#: Static files collection method (defaults to copying files).
COLLECT_STORAGE = 'flask_collect.storage.file'

# Accounts
# ========
#: Email address used as sender of account registration emails.
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
#: Email subject for account registration emails.
SECURITY_EMAIL_SUBJECT_REGISTER = _(
    "Welcome to Cuban Organizations Registry!")
#: Redis session storage URL.
ACCOUNTS_SESSION_REDIS_URL = 'redis://' + IP_REDIS + ':6379/1'
#: Enable session/user id request tracing. This feature will add X-Session-ID
#: and X-User-ID headers to HTTP response. You MUST ensure that NGINX (or other
#: proxies) removes these headers again before sending the response to the
#: client. Set to False, in case of doubt.
ACCOUNTS_USERINFO_HEADERS = True

# Celery configuration
# ====================

BROKER_URL = 'amqp://iroko:iroko@' + IP_RABBIT + ':5672/'
#: URL of message broker for Celery (default is RabbitMQ).
CELERY_BROKER_URL = 'amqp://iroko:iroko@' + IP_RABBIT + ':5672/'
#: URL of backend for result storage (default is Redis).
CACHE_REDIS_URL = 'redis://' + IP_REDIS + ':6379/0'
CACHE_TYPE = 'redis'

CELERY_RESULT_BACKEND = 'redis://' + IP_REDIS + ':6379/2'
#: Scheduled tasks configuration (aka cronjobs).
CELERY_BEAT_SCHEDULE = {
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'accounts': {
        'task': 'invenio_accounts.tasks.clean_session_table',
        'schedule': timedelta(minutes=60),
    },
}

SEARCH_ELASTIC_HOSTS='["http://"]'
params = dict(
    #    http_auth=('user', 'uRTbYRZH268G'),
)
SEARCH_ELASTIC_HOSTS = [
    dict(host=IP_ELASTIC, **params)
]

# Database
# ========
#: Database URI including user and password
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://cuor:cuor@' + IP_POSGRE + '/cuor'
# JSONSchemas
# ===========
#: Hostname used in URLs for local JSONSchemas.
JSONSCHEMAS_HOST = 'cuor.cu'

JSONSCHEMAS_ENDPOINT = '/schemas'
JSONSCHEMAS_HOST = os.environ.get('JSONSCHEMAS_HOST', 'localhost:5000')
JSONSCHEMAS_URL_SCHEME = 'https'

# Flask configuration
# ===================
# See details on
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

#: Secret key - each installation (dev, production, ...) needs a separate key.
#: It should be changed before deploying.
SECRET_KEY = 'cuor_secret_key'
#: Max upload size for form data via application/mulitpart-formdata.
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB
#: Sets cookie with the secure flag by default
SESSION_COOKIE_SECURE = True

# OAI-PMH
# =======
OAISERVER_ID_PREFIX = 'oai:cuor.cu:'

# Previewers
# ==========
#: Include IIIF preview for images.
PREVIEWER_PREFERENCE = ['iiif_image'] + BASE_PREFERENCE

# Debug
# =====
# Flask-DebugToolbar is by default enabled when the application is running in
# debug mode. More configuration options are available at
# https://flask-debugtoolbar.readthedocs.io/en/latest/#configuration

#: Switches off incept of redirects by Flask-DebugToolbar.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Configures Content Security Policy for PDF Previewer
# Remove it if you are not using PDF Previewer
APP_DEFAULT_SECURE_HEADERS['content_security_policy'] = {
    'default-src': ["'self'", "'unsafe-inline'"],
    'object-src': ["'none'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'font-src': ["'self'", "data:", "https://fonts.gstatic.com",
                 "https://fonts.googleapis.com"],
}

WSGI_PROXIES = 2

_ORG_CONVERTER = (
    'pid(orgid, record_class="cuor.organizations.api.OrganizationRecord")'
)

RECORDS_REST_ENDPOINTS = {
    'orgid': dict(
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
        item_route='/organizations/<{0}:pid_value>'.format(_ORG_CONVERTER),
        default_media_type='application/json',
        max_result_window=100000,
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
    orgid=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>',
        template='organizations/organization.html',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),
    orgid_previewer=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>/preview/<path:filename>',
        view_imp='invenio_previewer.views.preview',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),
    orgid_files=dict(
        pid_type=ORGANIZATION_PID_TYPE,
        route='/organizations/<pid_value>/files/<path:filename>',
        view_imp='invenio_records_files.utils.file_download_ui',
        record_class='cuor.organizations.api.OrganizationRecord',
    ),

)
"""Records UI for cuor."""

SEARCH_UI_SEARCH_API = '/api/organizations/'
SEARCH_UI_SEARCH_INDEX = 'organizations'
INDEXER_DEFAULT_DOC_TYPE = 'organization-v1.0.0'
INDEXER_DEFAULT_INDEX = 'organizations-organization-v1.0.0'
OAISERVER_RECORD_INDEX = 'organizations'

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/organizations/results.html'
"""Result list template."""

