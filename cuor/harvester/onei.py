import datetime
import json
import logging
import os
import traceback

import pandas as pd
from flask import current_app
from invenio_db import db
from invenio_pidstore.resolver import Resolver

from cuor.harvester.general import insert_in_cuor
from cuor.organizations.api import OrganizationRecord
from cuor.organizations.pidstore import ORGANIZATION_TYPE

logger = logging.getLogger('cuor-onei-harvester')

datadir = current_app.config['CUOR_DATA_DIRECTORY']


top_organizations = {
    "organismos": {
            "path": os.path.join(datadir, "onei/complementarios/c_orga.xlsx"),
            "sheet": "C_orga",
            "col": "ORGA",
            "id_type": "orgaid",
    },
    "uniones": {
        "path": os.path.join(datadir, "onei/complementarios/c_uniones_0.xlsx"),
        "sheet": "C_Uniones",
        "col": "UNI",
        "id_type": "uniid",
    }

}

lower_organizations = {
    "re0420": {
        "path": os.path.join(datadir, "onei/RE0420.xlsx"),
        "sheet": "RE0420",
        "id_type": "reup",
    },
    "cnoa0420": {
        "path": os.path.join(datadir, "onei/CNOA0420.xlsx"),
        "sheet": "CNOA0420",
        "id_type": "reup",
    },
    "me0420": {
        "path": os.path.join(datadir, "onei/ME0420.xlsx"),
        "sheet": "ME0420",
        "id_type": "reup",
    }
}

dpa_path = os.path.join(datadir, "onei/dpa.json")


def get_list_when_field_meet(path_item, col, value):
    lista = {}
    try:
        count = 0
        entrada = pd.read_excel(path_item["path"], path_item["sheet"])

        for archivo in entrada['COD']:
            if col in entrada.keys() and entrada[col][count] == value:
                lista[archivo] = {
                    'COD': archivo,
                    'DESCC': entrada['DESCC'][count],
                }
            count = count + 1
    except Exception as e:
        print(str(e))
    #print(lista)
    return lista


def get_organization_from(path_item, col, value):
    try:
        count = 0
        entrada = pd.read_excel(path_item["path"], path_item["sheet"])

        for archivo in entrada['COD']:
            if col in entrada.keys() and entrada[col][count] == value:
                item = {
                    'COD': archivo,
                    'DESCC': entrada['DESCC'][count],
                    'SIGLAS': entrada['SIGLAS'][count],
                    'DIRECC': entrada['DIRECC'][count],
                    'ALTA': entrada['ALTA'][count],
                    'DPA': entrada['DPA'][count],
                    'ORGA': entrada['ORGA'][count],
                    'UNI': entrada['UNI'][count],
                }
                return item
            count = count + 1
    except Exception as e:
        print(str(e))

    return {}


def get_top_organizations():
    try:
        for item in top_organizations.values():
            count=0
            entrada = pd.read_excel(item["path"], item["sheet"])
            if item["col"] == 'ORGA' or (item["col"] == 'UNI' and not str(entrada['CODIGO'][0]) == '999'):
                for archivo in entrada['CODIGO']:
                    las_siglas = []
                    siglas = str(entrada['CORTO'][count])
                    #print('siglas: ', str(siglas))
                    if not siglas.isalnum():
                        siglas = siglas.replace("-", "").strip()
                        #print("cambio: ", siglas)
                    if len(siglas) > 0:
                        las_siglas.append(siglas)
                    data = {
                        "name": entrada['DESC'][count],
                        "acronyms": las_siglas,
                        "addresses": [],
                        "labels": [{
                            "label": entrada['DESC'][count],
                            "iso639": "es",
                        }]
                    }

                    active = False
                    if "NOactivo" in entrada.keys() and not entrada['NOactivo'][count]:
                        active = True
                    if "Activo" in entrada.keys() and str.lower(entrada["Activo"][count]) != "no":
                        active = True

                    if active:
                        data["status"] = "active"
                    else:
                        data["status"] = "obsolete"

                    ids = []
                    ids.append({
                        'idtype': item["id_type"],
                        'value': str(item["id_type"]) + '.' + str(archivo)
                    })
                    data['identifiers'] = ids

                    data['relationships'] = []
                    for child_item in lower_organizations.values():
                        children = get_list_when_field_meet(child_item, col=item["col"], value=archivo)
                        if len(children) > 0:
                            for rel in children.values():
                                nrel = dict()
                                nrel['label'] = rel['DESCC']
                                nrel['type'] = 'child'
                                nrel['identifiers'] = [{
                                    'idtype': "reup",
                                    'value': "reup" + "." + str(rel['COD'])
                                }]
                                data['relationships'].append(nrel)

                    count = count+1
                    #print("*********************8")
                    #print("*********************8")
                    #print(data)
                    #print("*********************8")
                    print("*********************8")
                    logger.info("Going well creating top organization codigo: {}".format(archivo), extra=data)
                    insert_in_cuor(data, {})
    except Exception as e:
        print("*********************")
        print("Error adding top organizations")
        #print(str(e))
        print(traceback.format_exc())
        print("*********************")
        logger.exception(traceback.format_exc())


def get_lower_organizations():
    db.session.rollback()
    try:
        for item in lower_organizations.values():
            count=0
            entrada = pd.read_excel(item["path"], item["sheet"])

            for archivo in entrada['COD']:
                las_siglas = []
                siglas = str(entrada['SIGLAS'][count])
                #print('siglas: ', str(siglas))
                if not siglas.isalnum():
                    siglas = siglas.replace("-", "").strip()
                    #print("cambio: ", siglas)
                if len(siglas) > 0:
                    las_siglas.append(siglas)

                data = {
                    "name": entrada['DESCC'][count],
                    "acronyms": las_siglas,
                    "status": "active",
                    "labels": [{
                        "label": entrada['DESCC'][count],
                        "iso639": "es",
                    }]
                }

                date_str = entrada['ALTA'][count] # puede ser d/m/A o puede ser Amd
                datetime_obj = None

                if isinstance(date_str, datetime.datetime):
                    datetime_obj = date_str
                else:
                    try:
                        format_str1 = '%d/%m/%Y'  # The format
                        format_str2 = '%Y%m%d'  # The format
                        print(date_str)
                        datetime_obj = datetime.datetime.strptime(date_str, format_str1)
                    except:
                        try:
                            datetime_obj = datetime.datetime.strptime(date_str, format_str2)
                        except Exception as e:
                            print(str(e))

                if datetime_obj:
                    data['established'] = datetime_obj.date().year

                ids = []
                ids.append({
                    'idtype': item["id_type"],
                    'value': str(item["id_type"]) + '.' + str(archivo)
                })
                data['identifiers'] = ids

                #Falta el DPA, hay que revisar la tabla de transferencia para ver conversion de codigos
                #entrada['DPA'][count],

                cod_dpa = entrada['DPA'][count]
                cod_dpa = str(cod_dpa)
                prov = cod_dpa[0:2]
                addresses = []
                with open(dpa_path) as f:
                    dpa = json.load(f)
                    one_address = {}
                    if prov != '40':
                        one_address["city"] = dpa[prov]["municipalities"][cod_dpa]
                    else:
                        one_address["city"] = dpa[prov]["name"]
                    one_address["country"] = "Cuba"
                    one_address["country_code"] = "CU"
                    one_address["primary"] = True
                    one_address["state"] = dpa[prov]["name"]
                    one_address["state_code"] = dpa[prov]["iso"]

                    addresses.append(one_address)

                data['addresses'] = addresses

                #para las relationships debe hacerse algo parecido al resolver, ver que es
                relationships = []
                organism = None
                union = None

                resolver = Resolver(
                    pid_type=top_organizations["organismos"]["id_type"],
                    object_type=ORGANIZATION_TYPE,
                    getter=OrganizationRecord.get_record,
                )
                try:
                    pid_organism = top_organizations["organismos"]["id_type"] + "." + str(entrada['ORGA'][count])
                    pid_organism, organism = resolver.resolve(pid_organism)
                    if organism:
                        #print("pid: ", pid_organism)
                        #print("organismo: ", organism)
                        nrel = {}
                        nrel["label"] = organism["name"]
                        nrel["type"] = "parent"
                        nrel["identifiers"] = organism["identifiers"]
                        relationships.append(nrel)
                        #print("nrel:  ")
                        #print(nrel)
                        #print(relationships)
                except Exception as eo:
                    print(str(eo))

                try:
                    if str(entrada['UNI'][count]) != '999':
                        resolver.pid_type = top_organizations["uniones"]["id_type"]
                        pid_union = top_organizations["uniones"]["id_type"] + "." + str(entrada['UNI'][count])
                        pid_union, union = resolver.resolve(pid_union)
                        if union:
                            #print("pid: ", pid_union)
                            #print("union: ", union)
                            nrel = dict()
                            nrel['label'] = union['name']
                            nrel['type'] = 'parent'
                            nrel['identifiers'] = union["identifiers"]
                            relationships.append(nrel)
                            #print("nrel:  ")
                            #print(nrel)
                            #print(relationships)
                except Exception as eu:
                    print(str(eu))

                data['relationships'] = relationships
                count = count+1
                #print(data)
                insert_in_cuor(data, {})

    except Exception as e:
        print("*********************")
        print("Error adding lower organizations")
        print(str(e))
        print(traceback.format_exc())
        print("*********************")


def load_onei():
    pass


