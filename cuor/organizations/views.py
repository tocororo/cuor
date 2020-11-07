# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from operator import itemgetter
from os.path import splitext

from flask import Blueprint, request, jsonify
from invenio_previewer.proxies import current_previewer

from cuor.organizations.api import OrganizationRecord
from cuor.organizations.marshmallow import MetadataSchemaRelIDsV1
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


@api_blueprint.route('/<uuid>/relationships', methods=['GET'])
def get_organization_relationships(uuid):
    """Get a source by any PID received as a argument, including UUID"""
    try:
        # TODO: ver como optimizar esto
        # print("## 1- {0}".format(datetime.datetime.now().strftime("%H:%M:%S")))
        rtype = request.args.get('type') if request.args.get('type') else None
        pid, org = OrganizationRecord.get_org_by_pid(uuid)
        if not pid or not org:
            raise Exception('no uuid: {0}'.format(uuid))
        children = []
        # print("## 2- {0}".format(datetime.datetime.now().strftime("%H:%M:%S")))
        for rel in org['relationships']:
            pidvalue = rel['identifiers'][0]['value']
            rel_type = rel['type']
            pid, rel_org = OrganizationRecord.get_org_by_pid(pidvalue)
            if pid and rel_org:
                if rtype:
                    if rel_type == rtype:

                        children.append(json_v1.transform_record(pid, rel_org))
                else:
                    children.append(json_v1.transform_record(pid, rel_org))
            # print("## 2- 11 {0}".format(datetime.datetime.now().strftime("%H:%M:%S")))
        # print("## 3- {0}".format(datetime.datetime.now().strftime("%H:%M:%S")))
        # return json_v1_response(pid, org)
        children.sort(key=sortOrg)
        return jsonify(children)

    except Exception as e:
        return jsonify({
            'ERROR': str(e),
        })
