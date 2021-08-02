# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys

from SPARQLWrapper import SPARQLWrapper, JSON
from cuor.harvester.wikidata.logger_base import logger

endpoint_url = "https://query.wikidata.org/sparql"


def getSparqlEntities(QID):
    try:
        # Q43229 - organization
        query = """SELECT DISTINCT ?item  ?itemLabel ?itemDescription
                   ?country  ?countryLabel
            
                    WHERE {
                     ?item (wdt:P31)+ wd:""" f"{QID};" """
                                      rdfs:label ?itemLabel.
                        FILTER(lang(?itemLabel) = 'en')
                     
                        OPTIONAL { ?item  wdt:P17  ?country }      
                        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                     }
                     ORDER BY ?item"""

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()
    except Exception as e:
        logger.debug(f'ERROR: {e}')
        return None


def getSparqlOrganizations(QID):
    try:
        # Q43229 - organization
        query = """SELECT ?item ?itemLabel
                    WHERE { 
                          ?item (wdt:P279)* wd:""" f"{QID};" """
                                 rdfs:label ?itemLabel.
                          FILTER(lang(?itemLabel) = 'en')
                    }
                    ORDER BY ?item"""

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()
    except Exception as e:
        logger.debug(f'ERROR: {e}')
        return None


def getEntitiesStatements(itemLabel):
    query = """SELECT ?_prop ?propLabel ?_prop_entity ?_prop_entityLabel
                WHERE
                {
                    ?item rdfs:label """  f'"{itemLabel}"' " """"@en.
                    ?item ?_prop ?_prop_entity.

                    SERVICE wikibase:label { bd:serviceParam wikibase:language "es". } 
                    ?prop wikibase:directClaim ?_prop .
                }"""
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def getEntitiesDescription(itemLabel):
    try:
        # Q43229 - organization
        query = """SELECT DISTINCT ?item  ?itemLabel ?itemDescription ?itemAltLabel
            
                    WHERE {
                     ?item rdfs:label """  f'"{itemLabel}"' " """"@en.
                     OPTIONAL { ?item skos:altLabel ?alternative . }
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "es". }
                    }"""

        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()
    except Exception as e:
        logger.debug(f'ERROR: {e}')
        return None


if __name__ == '__main__':
    resultsOrganizations = getEntitiesStatements('Q43229')
    for result in resultsOrganizations["results"]["bindings"]:
        print(result)

# resultsOrganizations = getSparqlOrganizations('Q43229')
# for result in resultsOrganizations["results"]["bindings"]:
#     # subClass = Organizations(result.item.value)
#     print(result)

# resultsEntities = getSparqlEntities('Q43229')
# for result in resultsEntities["results"]["bindings"]:
#     # subClass = Organizations(result.item.value)
#     print(result)
