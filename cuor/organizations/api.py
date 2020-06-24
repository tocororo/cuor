# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

import traceback
from uuid import uuid4

from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.resolver import Resolver
from invenio_records_files.api import Record as FilesRecord
from invenio_indexer.api import RecordIndexer

from invenio_db import db

from cuor.organizations.pidstore import ORGANIZATION_PID_TYPE, ORGANIZATION_TYPE, IDENTIFIERS_FIELD, \
    identifiers_schemas, IDENTIFIERS_FIELD_TYPE, IDENTIFIERS_FIELD_VALUE, organization_uuid_minter, \
    identifiers_minter


class OrganizationRecord(FilesRecord):
    """Custom record."""

    _schema = "organizations/organization-v1.0.0.json"

    @classmethod
    def create_or_update(cls, org_uuid, data, dbcommit=False, reindex=False, **kwargs):
        """Create or update OrganizationRecord."""

        # assert org_uuid

        resolver = Resolver(
            pid_type=ORGANIZATION_PID_TYPE,
            object_type=ORGANIZATION_TYPE,
            getter=cls.get_record,
        )
        try:
            persistent_identifier, org = resolver.resolve(str(org_uuid))
            if org:
                print("{0}={1} found".format(ORGANIZATION_PID_TYPE, org_uuid))
                org.update(data, dbcommit=dbcommit, reindex=reindex)
                # .update(data, dbcommit=dbcommit, reindex=reindex)
                return org, 'updated'
        except Exception:
            pass
        if IDENTIFIERS_FIELD in data:
            for schema in identifiers_schemas:
                for identifier in data[IDENTIFIERS_FIELD]:
                    if schema == identifier[IDENTIFIERS_FIELD_TYPE]:
                        resolver.pid_type = schema
                        try:
                            persistent_identifier, org = resolver.resolve(str(identifier[IDENTIFIERS_FIELD_VALUE]))
                            print('<<<<<<<<<<<<<<<<<<')
                            print('Org= ', org)
                            if org:
                                print("{0}={1} found".format(schema, str(identifier[IDENTIFIERS_FIELD_VALUE])))
                                org.update(data, dbcommit=dbcommit, reindex=reindex)
                                print('>>>>>>>>>>>>>>>>>>>>')
                                print('org updated: ', org)
                                return org, 'updated'
                        except PIDDoesNotExistError as pidno:
                            print("PIDDoesNotExistError:  {0} == {1}".format(schema, str(identifier[IDENTIFIERS_FIELD_VALUE])))
                        except Exception as e:
                            print('-------------------------------')
                            print(str(e))
                            print(traceback.format_exc())
                            print('-------------------------------')
                            pass
        print("no pids found, creating organization")
        created_org = cls.create(data, id_=org_uuid, dbcommit=dbcommit, reindex=reindex)
        return created_org, 'created'

    def update(self, data, dbcommit=False, reindex=False,):
        """Update data for record."""
        super(OrganizationRecord, self).update(data)
        super(OrganizationRecord, self).commit()

        if dbcommit:
            db.session.commit()
            if reindex:
                RecordIndexer().index(self)

        return self

    @classmethod
    def create(cls, data, id_, dbcommit=False, reindex=False, **kwargs):
        """Create a new OrganizationRecord."""
        data['$schema'] = current_jsonschemas.path_to_url(cls._schema)

        if not id_:
            id_ = uuid4()

        organization_uuid_minter(id_, data)

        identifiers_minter(id_, data, ORGANIZATION_TYPE)

        org = super(OrganizationRecord, cls).create(data=data, id_=id_, **kwargs)

        if dbcommit:
            db.session.commit()
            if reindex:
                RecordIndexer().index(org)
        return org

