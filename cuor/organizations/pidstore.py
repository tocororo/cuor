from invenio_pidstore.errors import PIDDoesNotExistError, PIDAlreadyExists
from invenio_pidstore.fetchers import FetchedPID
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.base import BaseProvider
from uuid import uuid4

ORGANIZATION_PID_TYPE = "recid"
ORGANIZATION_PID_MINTER = "recid"
ORGANIZATION_PID_FETCHER = "recid"
ORGANIZATION_PID_FIELD = "id"
ORGANIZATION_TYPE = "org"

IDENTIFIERS_FIELD = "identifiers"
IDENTIFIERS_FIELD_TYPE = "idtype"
IDENTIFIERS_FIELD_VALUE = "value"


identifiers_schemas = [
        "grid",
        "wkdata",
        "ror",
        "isni",
        "fudref",
        "orgref",
        "reup"
    ]


def get_identifier_schema(pid):

    for schema in identifiers_schemas:
        if schema in pid:
            return schema
    return None


class OrganizationUUIDProvider(BaseProvider):

    pid_type = ORGANIZATION_PID_TYPE
    pid_provider = None
    default_status = PIDStatus.REGISTERED

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier from the depoist PID value."""
        if 'pid_value' not in kwargs:
            kwargs.setdefault('pid_value', str(uuid4()))
        kwargs.setdefault('status', cls.default_status)
        return super(OrganizationUUIDProvider, cls).create(
            object_type=object_type, object_uuid=object_uuid, **kwargs)


def organization_uuid_minter(org_uuid, data):
    assert ORGANIZATION_PID_FIELD not in data

    provider = OrganizationUUIDProvider.create(
        object_type=ORGANIZATION_TYPE,
        object_uuid=org_uuid,
    )
    data[ORGANIZATION_PID_FIELD] = provider.pid.pid_value

    return provider.pid


def organization_uuid_fetcher(org_uuid, data):
    return FetchedPID(
        provider=OrganizationUUIDProvider,
        pid_type=OrganizationUUIDProvider.pid_type,
        pid_value=str(data[ORGANIZATION_PID_FIELD]),
    )


# A partir de aqui se puede crear un modulo que generalice todo esto.

def get_pid_by_data(data):
    """
    get pid or none,
    seek the IDENTIFIERS_FIELD in data, and then try to get PersistentIdentifier
    using any IDENTIFIERS_FIELD_TYPE, if a PID is found is returned
    else return None
    """
    assert IDENTIFIERS_FIELD in data
    for ids in data[IDENTIFIERS_FIELD]:
        if ids[IDENTIFIERS_FIELD_TYPE] in identifiers_schemas:
            try:
                pid = PersistentIdentifier.get(ids[IDENTIFIERS_FIELD_TYPE], ids[IDENTIFIERS_FIELD_VALUE])
                return pid
            except Exception:
                pass
    return None


def check_data_identifiers(data):
    """
    check if identifiers field is present in data, and then check if any on the PIDs
    not exists...
    """
    # print('IDENTIFIERS_FIELD in data {0}'.format(data))
    assert IDENTIFIERS_FIELD in data
    # print(data)
    for ids in data[IDENTIFIERS_FIELD]:
        if ids[IDENTIFIERS_FIELD_TYPE] in identifiers_schemas:
            try:
                pid = PersistentIdentifier.get(ids[IDENTIFIERS_FIELD_TYPE], ids[IDENTIFIERS_FIELD_VALUE])
                raise PIDAlreadyExists(pid_type=ids[IDENTIFIERS_FIELD_TYPE], pid_value=ids[IDENTIFIERS_FIELD_VALUE])
            except PIDDoesNotExistError:
                pass
    return True


class IdentifiersProvider(BaseProvider):
    default_status = PIDStatus.REGISTERED

    @classmethod
    def create_identifiers(cls, object_type=None, object_uuid=None, data=None,  **kwargs):

        assert data, "no data"
        assert IDENTIFIERS_FIELD in data
        pIDs = []
        for ids in data[IDENTIFIERS_FIELD]:
            if ids['idtype'] in identifiers_schemas:
                provider = super(IdentifiersProvider, cls).create(
                    pid_type=ids['idtype'],
                    pid_value=ids['value'],
                    object_type=object_type,
                    object_uuid=object_uuid,
                    status=cls.default_status,
                    **kwargs
                )
                pIDs.append(provider.pid)
        return pIDs

    @classmethod
    def create_pid(cls, pid_type, object_type=None, object_uuid=None, data=None,  **kwargs):
        assert data, "no data"
        assert IDENTIFIERS_FIELD in data
        assert pid_type
        assert pid_type in identifiers_schemas
        for ids in data[IDENTIFIERS_FIELD]:
            if ids['idtype'] == pid_type:
                provider = super(IdentifiersProvider, cls).create(
                    pid_type=ids['idtype'],
                    pid_value=ids['value'],
                    object_type=object_type,
                    object_uuid=object_uuid,
                    status=cls.default_status,
                    **kwargs
                )
                return provider.pid


def identifiers_fetcher(record_uuid, data, pid_type):
    assert data, "no data"
    assert IDENTIFIERS_FIELD in data
    for schema in identifiers_schemas:
        if schema == pid_type:
            return FetchedPID(
                provider=IdentifiersProvider,
                pid_type=pid_type,
                pid_value=data[IDENTIFIERS_FIELD][schema]
                )


def identifiers_minter(uuid, data, object_type):
    prsIDs = IdentifiersProvider.create_identifiers(
        object_type=object_type,
        object_uuid=uuid,
        data=data
    )
    return prsIDs
