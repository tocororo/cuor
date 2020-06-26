import json
import os
from flask import current_app
from cuor.harvester.general import remove_nulls,_assing_if_exist, insert_in_cuor


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

            insert_in_cuor(data, inst)


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


