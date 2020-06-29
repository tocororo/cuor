from cuor.organizations.api import OrganizationRecord
import traceback

def remove_nulls(d):
    return {k: v for k, v in d.items() if v is not None}


def _assing_if_exist(data, record, field):
    if field in record:
        data[field] = record[field]


def insert_in_cuor(data, inst):
    try:
        OrganizationRecord.create_or_update(None, data, dbcommit=True, reindex=True)
    except Exception as e:
        print(e)
        print("------------")
        #print(data)
        #print("------------")
        #print(inst)
        #print("------------")
        #print(traceback.format_exc())
