# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from __future__ import absolute_import, print_function

from flask import Blueprint, render_template, session
from flask_login import current_user

blueprint = Blueprint(
    'cuor',
    __name__,
    template_folder='templates',
    static_folder='static',
)


# @blueprint.route('/', methods=['GET'])
@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def index(path):
    print(session)
    print(path)
    if current_user.is_authenticated:
        return render_template('cuor/frontpage.html',
                           user=current_user)
    else:
        return render_template('cuor/frontpage.html')
