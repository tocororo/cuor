# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UPR.
#
# CuOR is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

import traceback
from copy import deepcopy
from uuid import uuid4

from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.errors import PIDDoesNotExistError, PIDDeletedError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from sqlalchemy.orm.exc import NoResultFound

from cuor.organizations.pidstore import (
    ORGANIZATION_PID_TYPE, ORGANIZATION_TYPE, IDENTIFIERS_FIELD,
    identifiers_schemas, IDENTIFIERS_FIELD_TYPE, IDENTIFIERS_FIELD_VALUE, organization_uuid_minter,
    identifiers_minter,
)


# TODO: cuando se actualiza una organizacion y se pone status: "redirected"
#  no aparece la informacion de a cual redirecciona.... incluir esto...



class OrganizationRecord(Record):
    """Custom record."""

    _schema = "organizations/organization-v1.0.0.json"

    @classmethod
    def create_or_update(cls, org_uuid, data, dbcommit=False, reindex=False, **kwargs):
        """Create or update OrganizationRecord."""

        # assert org_uuid
        org, msg = cls.resolve_and_update(org_uuid, data, dbcommit, reindex)
        #if resolve_and_update do no retunr, then is not existed org, so trying to create one
        if not org:
            print("no pids found, creating organization")
            created_org = cls.create(data, id_=org_uuid, dbcommit=dbcommit, reindex=reindex)
            org = created_org
            msg = 'created'

        return org, msg

    @classmethod
    def __delete_pids_without_object(cls, pid_list):
        try:
            # print('pids list: ')
            # print(pid_list)
            if pid_list and len(pid_list) > 0:
                for identifier in pid_list:
                    pid_type = identifier[IDENTIFIERS_FIELD_TYPE]
                    pid_value = identifier[IDENTIFIERS_FIELD_VALUE]
                    # print('pid type deleting: ')
                    # print(pid_type)
                    # print(pid_value)
                    pid_item = PersistentIdentifier.get(pid_type, pid_value)
                    pid_item.status = PIDStatus.NEW
                    #print('getting pid item: ')

                    if pid_item.delete():
                        db.session.commit()
                        #print("***************** DELETED!!!!")
        except Exception as e:
            print("-------- DELETING PID ERROR ------------")
            print(traceback.format_exc())

    @classmethod
    def resolve_and_update(cls, org_uuid, data, dbcommit=False, reindex=False, **kwargs):
        print("first in resolve and update ==============================")
        print(data)
        print("===========================================================")
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
        if IDENTIFIERS_FIELD in data: #Si no lo encontro por el uudi igual se intenta buscar desde cualquier otri pid
            for schema in identifiers_schemas:
                for identifier in data[IDENTIFIERS_FIELD]:
                    if schema == identifier[IDENTIFIERS_FIELD_TYPE]:
                        # print("identifier ------    ", identifier)
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
                            print("PIDDoesNotExistError:  {0} == {1}".format(schema,
                                                                             str(identifier[IDENTIFIERS_FIELD_VALUE])))
                        except (PIDDeletedError, NoResultFound) as ex:
                            cls.__delete_pids_without_object(data[IDENTIFIERS_FIELD])
                        except Exception as e:
                            print('-------------------------------')
                            # print(str(e))
                            print(traceback.format_exc())
                            print('-------------------------------')
                            pass

    def update(self, data, dbcommit=False, reindex=False,):
        """Update data for record."""

        self.updating_relations_from_existed(data)
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

    @classmethod
    def get_org_by_pid(cls, pid_value, with_deleted=False):
        resolver = Resolver(
            pid_type=ORGANIZATION_PID_TYPE,
            object_type=ORGANIZATION_TYPE,
            getter=cls.get_record,
        )
        try:
            return resolver.resolve(str(pid_value))
        except Exception:
            pass

        for pid_type in identifiers_schemas:
            try:
                resolver.pid_type = pid_type
                schemapid, org = resolver.resolve(pid_value)
                pid = PersistentIdentifier.get(ORGANIZATION_PID_TYPE, org['id'])
                return pid, org
            except Exception as e:
                pass
        return None, None

    @classmethod
    def active_org_resolver(cls, pid_value, with_deleted=False):
        """
        Este metodo es en esencia muy similar a get_org_by_pid, primeramente obtiene el objeto org
        usando cualquiera de los identificadores como filtro de busqueda,
        pero adicionalmente comprueba que el estado de la org resultante es activo, si fuere redirected
        pues la org que devuelve es dicha org apunta,
        en caso de que no tenga registrado en el campo redirected a quien apunta emite Error
        en caso que se solicita una org cuyo estado es obsolete emite error 400
        """
        try:
            pid, org = cls.get_org_by_pid(pid_value, with_deleted)
            if (org["status"] == "redirected"):
                if ("redirect" not in org):
                    raise Exception("No se han especificados los datos de la organizacion a quien redirecciona.")

                real_org_pid = org["redirect"]["value"]
                pid, org = cls.active_org_resolver(real_org_pid, with_deleted)

            return pid, org
        except Exception as e:
            print("error> ", str(e))
            pass
        return None, None

    @classmethod
    def check_organization_before_crud(cls, uuid, data, adding=False, on_demand=False):
        """
        Este metodo debe ser capaz de revisar las cuestiones de reglas de negocios para la adicion
        y para la modificacion de metadatos de la organizacion
        param data es el json de la org
        param adding dice si esta en la accion de adicionar o de editar
        La estructura del json no hay q validarla, eso lo hace el metodo commit.

        debe verificar si es adicionar:
        si es cubana que no tenga incluido entre los datos q se quieren adicionar reup, ni orgaid, ni uniid
        (estos datos solo se toman desde la ONEI)
        debe tener como parent alguna org con reup, no se permite adicionar org de primer nivel

        debe verificar cuando modifica que no cambia el reup si existe

        """

        return True

    def updating_relations_from_existed(self, data):

        org = self
        if org:
            if 'relationships' not in org:
                org["relationships"] = []
            if 'relationships' not in data:
                data["relationships"] = []
            lost_relations = list(org["relationships"])
            new_relations = list(data["relationships"])

            for old_item in org["relationships"]:
                exist = False
                #no usar lista.remove porque puede haber diferencia en el campo identifiers y se la misma org
                old_aux = new_aux = None
                for new_item in data["relationships"]:
                    if "id" in old_item:
                        old_aux = old_item["id"]
                    if "id" in new_item:
                        new_aux = new_item["id"]
                    #tuve q usar estos aux porque hay errores en los datos de la base de datos en el campop relationships
                    #no esta el id en ocasiones
                    if old_aux and new_aux and  old_aux == new_aux and old_item["type"] == new_item["type"]:
                        exist = True
                        new_relations.remove(new_item)
                        lost_relations.remove(old_item)
                        #si existe en las relaciones que ya tenia, no interesa si la nueva viene con mas pids
                        #el final esta y por el uuid se recupera, pero si cambia el tipo de relacion
                        #se agrega como una nueva, eliminando la anterior que es la misma org pero con diferente tipo
                        next()
            actual = {
                "id" : data["id"],
                "identifiers" : data["identifiers"],
                "label" : data["name"]
            }
            print("actuallllllllllllllllllllllllllllll")
            print(actual)
            print("````````````````````````````````````")
            self.deleting_relations(lost_relations, actual)
            self.adding_relations(new_relations, actual)


    def deleting_relations(self, lost_relations, actual):
        """
        param lost_relations tiene los elementos del campo relationships que ya no estaran mas en la org,
        la idea es recorrer cada una de estas orgs e informarles que ya no tienen relacion,
        param actual ofrece un dict q solo falta el type de relation para que pueda ser usado al encontrar indice
        param resolver es capaz de resolver dado un uuid la organizacion
        """

        for relation in lost_relations:
            pid = ""
            if "id" in relation:
                pid = relation["id"]
            elif "identifiers" in relation and len(relation["identifiers"]) > 0:
                pid = relation["identifiers"][0]["value"]
            #hice esto anterior por errores en los datos en la base de datos
            persistent_identifier, org = OrganizationRecord.get_org_by_pid(pid)
            if org:
                print("--------------deleting relationships--------------------------")
                if relation["type"] == "parent":
                    actual["type"] = "child"
                elif relation["type"] == "child":
                    actual["type"] = "parent"
                else:
                    actual["type"] = relation["type"]
                print(actual)

                rels = org["relationships"]
                try:
                    rels.remove(actual)
                    org.commit()
                except ValueError:
                    print("ValueError, porque no esta en la lista de relaciones")
                    pass
                print(org)
                print("-----------------------------------------------------------------")
                # .update(data, dbcommit=dbcommit, reindex=reindex)

    def adding_relations(self, new_relations, actual):
        """
        param new_relations nuevas orgs con las que tendra actual relacion,
        debe informarse a cada una de su nueva relacion
        param actual ofrece un dict q solo falta el type de relation para que pueda ser usado al encontrar indice
        """

        for relation in new_relations:
            pid = ""
            if "id" in relation:
                pid = relation["id"]
            elif "identifiers" in relation and len(relation["identifiers"]) > 0:
                pid = relation["identifiers"][0]["value"]
            # hice esto anterior por errores en los datos en la base de datos
            persistent_identifier, org = OrganizationRecord.get_org_by_pid(pid)

            if org:
                print("--------------adding relationships--------------------------")
                print(org)
                print("===============")
                print("{0}={1} found".format(org["name"], relation["id"]))
                if relation["type"] == "parent":
                    actual["type"] = "child"
                elif relation["type"] == "child":
                    actual["type"] = "parent"
                else:
                    actual["type"] = relation["type"]
                print(actual)

                org["relationships"].append(actual)
                print(org)
                print("-----------------------------------------------------------------")
                org.commit()
                # .update(data, dbcommit=dbcommit, reindex=reindex)

