# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

import datetime
from functools import wraps
from operator import itemgetter
from os.path import splitext

from flask import Blueprint, request, jsonify, abort, current_app
from flask_login import current_user, login_required
from invenio_cache import current_cache
from invenio_oauth2server.models import Client
from invenio_oauth2server.provider import oauth2
from invenio_oauth2server.views.server import error_handler as oauth_error_handler, authorize as oauth_authorized
from invenio_previewer.proxies import current_previewer

from cuor.organizations.api import OrganizationRecord
from cuor.organizations.marshmallow import MetadataSchemaRelIDsV1
from cuor.organizations.permissions import curator_permission
from cuor.organizations.serializers import json_v1_response, json_v1

blueprint = Blueprint(
    'cuor_organizations',
    __name__,
    template_folder='templates',
    static_folder='static',
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

#
# Views
#
@blueprint.route('/cuor/authorize', methods=['GET', 'POST'])
# @register_breadcrumb(blueprint, '.', _('Authorize application'))
@login_required
@oauth_error_handler
@oauth2.authorize_handler
def authorize(*args, **kwargs):
    """View for rendering authorization request."""
    if request.method == 'GET':
        client = Client.query.filter_by(
            client_id=kwargs.get('client_id')
        ).first()

        if not client:
            abort(404)
        internal_apps = current_app.config['INTERNAL_CLIENT_APPS_SECRETS']
        if client.client_secret in internal_apps:
            return True

    return oauth_authorized(*args, **kwargs)



#
# Files related template filters.
#
@blueprint.app_template_filter()
def select_preview_file(files):
    """Get list of files and select one for preview."""
    selected = None

    try:
        for f in sorted(files or [], key=itemgetter('key')):
            file_type = splitext(f['key'])[1][1:].lower()
            if file_type in current_previewer.previewable_extensions:
                if selected is None:
                    selected = f
                elif f['default']:
                    selected = f
    except KeyError:
        pass
    return selected


def check_permission(fn):
    """Check user permissions."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        """Decorated view."""
        if not current_user.is_authenticated:
            abort(401)
        if not curator_permission.can():
            abort(403)
        return fn(*args, **kwargs)
    return decorated_view


api_blueprint = Blueprint(
    'cuor_api_organizations',
    __name__,
    url_prefix='/organizations'
)


@api_blueprint.route('/pid', methods=['GET'])
def get_org_by_pid():
    """Get a source by any PID received as a argument, including UUID"""
    try:
        _id = request.args.get('value')
        pid, org = OrganizationRecord.get_org_by_pid(_id)
        if not pid or not org:
            raise Exception('')

        return json_v1_response(pid, org)
        # return jsonify(json_v1.serialize(pid, org))

    except Exception as e:
        return jsonify({
            'no pid found': _id,
        })


organizations_schema_many = MetadataSchemaRelIDsV1(many=True)


def sortOrg(org):
    return org['metadata']['name']

def _get_organization_relationships(uuid, rtype):
    pid, org = OrganizationRecord.get_org_by_pid(uuid)
    if not pid or not org:
        raise Exception('no uuid: {0}'.format(uuid))
    children = []
    for rel in org['relationships']:
        pidvalue = rel['identifiers'][0]['value']
        rel_type = rel['type']
        pid, rel_org = OrganizationRecord.get_org_by_pid(pidvalue)
        if pid and rel_org:
            if rtype:
                if rtype == rel_type:
                    children.append(json_v1.transform_record(pid, rel_org))
            else:
                children.append(json_v1.transform_record(pid, rel_org))
    children.sort(key=sortOrg)
    return children


@api_blueprint.route('/<uuid>/relationships', methods=['GET'])
def get_organization_relationships(uuid):
    """Get a source by any PID received as a argument, including UUID"""
    try:
        rtype = request.args.get('type') if request.args.get('type') else None
        cache = current_cache.get("get_organization_relationships:{0}{1}".format(uuid, rtype)) or {}
        if "date" not in cache:
            cache["date"] = datetime.datetime.now()
        if datetime.datetime.now() - cache["date"] < datetime.timedelta(days=1) and "stats" in cache:
            result = cache["stats"]
            return jsonify(result)
        else:
            result = _get_organization_relationships(uuid, rtype)
            cache["date"] = datetime.datetime.now()
            cache["stats"] = result
            current_cache.set("get_organization_relationships:{0}{1}".format(uuid, rtype), cache, timeout=-1)
            return jsonify(result)

    except Exception as e:
        return jsonify({
            'ERROR': str(e),
        })
