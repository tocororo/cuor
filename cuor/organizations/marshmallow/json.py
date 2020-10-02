# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.schemas import Nested, StrictKeysMixin
from invenio_records_rest.schemas.fields import (
    GenFunction,
    PersistentIdentifier, SanitizedUnicode,
)
from marshmallow import fields, missing, validate, post_dump

from cuor.organizations.api import OrganizationRecord


def bucket_from_context(_, context):
    """Get the record's bucket from context."""
    record = (context or {}).get('record', {})
    return record.get('_bucket', missing)


def files_from_context(_, context):
    """Get the record's files from context."""
    record = (context or {}).get('record', {})
    return record.get('_files', missing)


def schema_from_context(_, context):
    """Get the record's schema from context."""
    record = (context or {}).get('record', {})
    return record.get(
        "_schema",
        current_jsonschemas.path_to_url(OrganizationRecord._schema)
    )


class PersonIdsSchemaV1(StrictKeysMixin):
    """Ids schema."""

    source = SanitizedUnicode()
    value = SanitizedUnicode()


class IdentifierSchemaV1(StrictKeysMixin):
    """Ids schema."""

    idtype = SanitizedUnicode()
    value = SanitizedUnicode()


class LabelSchemaV1(StrictKeysMixin):
    """Ids schema."""

    label = SanitizedUnicode()
    iso639 = SanitizedUnicode()


class RelationSchemaV1(StrictKeysMixin):
    """Ids schema."""

    id = fields.UUID(dump_only=True)
    identifiers = Nested(IdentifierSchemaV1, many=True, required=True)
    type = SanitizedUnicode()
    label = SanitizedUnicode()

    @post_dump
    def dump_id(self, relationship, **kwargs):
        pidvalue = relationship['identifiers'][0]['value']
        pid, org = OrganizationRecord.get_org_by_pid(pidvalue)
        if pid and org:
            relationship['id'] = str(pid.pid_value)
        return relationship


class AddressSchemaV1(StrictKeysMixin):
    """Ids schema."""

    city = SanitizedUnicode()
    country = SanitizedUnicode()
    country_code = SanitizedUnicode()
    lat = fields.Float()
    lng = fields.Float()
    line_1 = SanitizedUnicode()
    line_2 = SanitizedUnicode()
    line_3 = SanitizedUnicode()
    postcode = SanitizedUnicode()
    primary = SanitizedUnicode()
    state = SanitizedUnicode()
    state_code = SanitizedUnicode()



class MetadataSchemaV1(StrictKeysMixin):
    """Schema for the record metadata."""

    id = PersistentIdentifier()
    identifiers = Nested(IdentifierSchemaV1, many=True, required=True)
    name = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    status = SanitizedUnicode()
    aliases = fields.List(SanitizedUnicode(), many=True)
    acronyms = fields.List(SanitizedUnicode(), many=True)
    types = fields.List(SanitizedUnicode(), many=True)
    wikipedia_url = fields.Url()
    email_address = fields.Email()
    ip_addresses = fields.String()
    established = fields.Integer()
    links = fields.List(fields.Url(), many=True)
    labels = Nested(LabelSchemaV1, many=True)
    relationships = Nested(RelationSchemaV1, many=True)
    addresses = Nested(AddressSchemaV1, many=True)

    _schema = GenFunction(
        attribute="$schema",
        data_key="$schema",
        deserialize=schema_from_context,  # to be added only when loading
    )


class RecordSchemaV1(StrictKeysMixin):
    """Record schema."""

    metadata = fields.Nested(MetadataSchemaV1)
    created = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)
    links = fields.Dict(dump_only=True)
    id = PersistentIdentifier()
    files = GenFunction(
        serialize=files_from_context, deserialize=files_from_context)
