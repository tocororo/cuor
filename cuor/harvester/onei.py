import pandas as pd
import datetime
import traceback
from cuor.harvester.general import insert_in_cuor

top_organizations = {
    "organismos": {
            "path": "data/onei/complementarios/c_orga.xlsx",
            "sheet": "C_orga",
            "col": "ORGA",
            "id_type": "orgaid",
    },
    "uniones": {
        "path": "data/onei/complementarios/c_uniones_0.xlsx",
        "sheet": "C_Uniones",
        "col": "UNI",
        "id_type": "uniid",
    }

}

lower_organizations = {
    "re0420": {
        "path": "data/onei/RE0420.xlsx",
        "sheet": "RE0420",
        "id_type": "reup",
    },
    "cnoa0420": {
        "path": "data/onei/CNOA0420.xlsx",
        "sheet": "CNOA0420",
        "id_type": "reup",
    },
    "me0420": {
        "path": "data/onei/ME0420.xlsx",
        "sheet": "ME0420",
        "id_type": "reup",
    }
}


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

            for archivo in entrada['CODIGO']:
                siglas = entrada['CORTO'][count]
                sig = []
                sig.extend(siglas.replace("-", "").strip())

                data = {
                    "name": entrada['DESC'][count],
                    "acronyms": sig,
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
                    'value': item["id_type"] + '.' + str(archivo)
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
                                'idtype': item["id_type"],
                                'value': str(item["id_type"]) + "." + str(rel['COD'])
                            }]
                            data['relationships'].append(nrel)

                count = count+1
                print("*********************8")
                print("*********************8")
                print(data)
                print("*********************8")
                print("*********************8")
                insert_in_cuor(data, {})
    except Exception as e:
        print("*********************")
        print("Error adding top organizations")
        print(str(e))
        print(traceback.format_exc())
        print("*********************")


def get_lower_organizations():

    try:
        for item in lower_organizations.values():
            count=0
            entrada = pd.read_excel(item["path"], item["sheet"])

            for archivo in entrada['COD']:

                siglas = entrada['SIGLAS'][count]
                siglas = siglas.replace("-", "").strip()

                data = {
                    "name": entrada['DESCC'][count],
                    "acronyms": siglas,
                    "status": "active",
                    "labels": {
                        "label": entrada['DESCC'][count],
                        "iso639": "es",
                    }
                }

                date_str = entrada['ALTA'][count] # puede ser d/m/A o puede ser Amd
                format_str1 = '%d/%m/%Y'  # The format
                format_str2 = '%Y%m%d'  # The format
                datetime_obj = None
                try:
                    datetime_obj = datetime.datetime.strptime(date_str, format_str1)
                except:
                    try:
                        datetime_obj = datetime.datetime.strptime(date_str, format_str2)
                    except Exception as e:
                        print(str(e))

                if datetime_obj:
                    data["established"] = str(datetime_obj.date().year)

                ids = []
                ids.append({
                    'idtype': item["id_type"],
                    'value': item["id_type"] + '.' + str(archivo)
                })
                data['identifiers'] = ids

                #Falta el DPA, hay que revisar la tabla de transferencia para ver conversion de codigos
                #entrada['DPA'][count],

                #para las relationships debe hacerse algo parecido al resolver, ver que es
                data['relationships'] = []
                organism = None
                union = None
                #pid_orga, organism = resolver.resolve(
                #    top_organizations["organismos"]["id_type"] + '.' + str(entrada['ORGA'][count])
                #)
                #pid_uni, union = resolver.resolve(
                #    top_organizations["uniones"]["id_type"] + '.' + str(entrada['UNI'][count])
                #)

                if organism:
                    nrel = dict()
                    nrel['label'] = organism['label']
                    nrel['type'] = 'parent'
                    nrel['identifiers'] = organism["identifiers"]
                    data['relationships'].append(nrel)

                if union:
                    nrel = dict()
                    nrel['label'] = union['label']
                    nrel['type'] = 'parent'
                    nrel['identifiers'] = union["identifiers"]
                    data['relationships'].append(nrel)

                count = count+1
                print(data)
                insert_in_cuor(data, {})

    except Exception as e:
        print("*********************")
        print("Error adding lower organizations")
        print(str(e))
        print(traceback.format_exc())
        print("*********************")


def load_onei():
    pass


