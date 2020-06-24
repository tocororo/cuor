import json
import os
from flask import current_app


from cuor.organizations.api import OrganizationRecord


def remove_nulls(d):
    return {k: v for k, v in d.items() if v is not None}


def _assing_if_exist(data, record, field):
    if field in record:
        data[field] = record[field]


def _get_ids(inst, idname, idcode):
    ids = []
    if 'external_ids' in inst and idname in inst['external_ids']:
        for id_ in inst['external_ids'][idname]['all']:
            ids.append({
                'idtype': idcode,
                'value': id_
            })
    return ids


def load_active(grid):
    for inst in grid['institutes']:
        if 'status' in inst and inst['status'] == 'active':
            # inst = grid['institutes'][0]
            data = dict()
            _assing_if_exist(data, inst, 'name')
            _assing_if_exist(data, inst, 'status')
            _assing_if_exist(data, inst, 'aliases')
            _assing_if_exist(data, inst, 'acronyms')
            _assing_if_exist(data, inst, 'types')
            _assing_if_exist(data, inst, 'wikipedia_url')
            _assing_if_exist(data, inst, 'email_address')
            _assing_if_exist(data, inst, 'ip_addresses')
            _assing_if_exist(data, inst, 'established')
            _assing_if_exist(data, inst, 'links')
            _assing_if_exist(data, inst, 'labels')
            _assing_if_exist(data, inst, 'addresses')

            arr = []
            if 'relationships' in inst:
                for rel in inst['relationships']:
                    nrel = dict()
                    nrel['label'] = rel['label']
                    nrel['type'] = str.lower(rel['type'])
                    nrel['identifiers'] = [{
                        'idtype': 'grid',
                        'value': rel['id']
                    }]
                    arr.append(nrel)
                data['relationships'] = arr

            ids = []
            ids.append({
                'idtype': 'grid',
                'value': inst['id']
            })
            ids.extend(_get_ids(inst, 'ISNI', 'isni'))
            ids.extend(_get_ids(inst, 'FundRef', 'fudref'))
            ids.extend(_get_ids(inst, 'OrgRef', 'orgref'))
            ids.extend(_get_ids(inst, 'Wikidata', 'wkdata'))
            ids.extend(_get_ids(inst, 'ROR', 'ror'))
            data['identifiers'] = ids
            try:
                OrganizationRecord.create_or_update(None, data, dbcommit=True, reindex=True)
            except Exception as e:
                print(e)
                print("------------")
                print(data)
                print("------------")
                print(inst)
                print("------------")


def load_redirect(grid):

    # TODO: add a new grid PID to the corresponding existing organization record.
    for inst in grid['institutes']:
        if 'status' in inst and inst['status'] == 'redirected':
            print(inst)


def load_grid():
    datadir = current_app.config['CUOR_DATA_DIRECTORY']

    with open(os.path.join(datadir, 'grid', 'grid.json')) as grid_path:
        grid = json.load(grid_path, object_hook=remove_nulls)
        load_active(grid)
        load_redirect(grid)


