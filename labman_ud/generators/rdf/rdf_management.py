# -*- encoding: utf-8 -*-


# Python 3 compatibility support
import sys

if sys.version_info[0] >= 3:
    import urllib as urllib2
else:
    import urllib
    import urllib2


from rdflib import Graph
from rdflib.namespace import Namespace, FOAF, DC, XSD, RDF, RDFS

from django.conf import settings

BIBO = Namespace('http://purl.org/ontology/bibo/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
GEONAMES = Namespace('http://www.geonames.org/ontology#')
MUTO = Namespace('http://purl.org/muto/core#')
PLACES = Namespace('http://purl.org/ontology/places#')
SWRC = Namespace('http://swrc.ontoware.org/ontology#')
SWRCFE = Namespace('http://www.morelab.deusto.es/ontologies/swrcfe#')


def create_namespaced_graph():
    graph = Graph()

    graph.bind('bibo', BIBO)
    graph.bind('dc', DC)
    graph.bind('dcterms', DCTERMS)
    graph.bind('foaf', FOAF)
    graph.bind('geonames', GEONAMES)
    graph.bind('muto', MUTO)
    graph.bind('places', PLACES)
    graph.bind('rdf', RDF)
    graph.bind('rdfs', RDFS)
    graph.bind('swrc', SWRC)
    graph.bind('swrcfe', SWRCFE)
    graph.bind('xsd', XSD)

    return graph


def _perform_request(query):

    try:
        url = getattr(settings, 'SPARQL_ENDPOINT_URL', None)

        if getattr(settings, 'SPARQL_ENDPOINT_AUTH', False):
            realm = getattr(settings, 'SPARQL_ENDPOINT_REALM', None)
            user = getattr(settings, 'SPARQL_ENDPOINT_USER', None)
            password = getattr(settings, 'SPARQL_ENDPOINT_PASSWORD', None)

            authhandler = urllib2.HTTPDigestAuthHandler()
            authhandler.add_password(realm, url, user, password)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)

        data = urllib.urlencode({'query': query})
        request = urllib2.Request(url, data)
        urllib2.urlopen(request)

    except:
        print(u'Unable to perform HTTP request over SPARQL endpoint')
        print(query, '\n')


def insert_by_post(graph):
    triples = ''

    for s, p, o in graph.triples((None, None, None)):
        triple = "%s %s %s . " % (s.n3(), p.n3(), o.n3())
        triples += triple

    query = 'INSERT IN GRAPH <%s> { %s }' % (getattr(settings, 'GRAPH_BASE_URL', None), triples.encode('utf-8'))

    _perform_request(query)


def delete_resource(resource_uri):
    query = """
        WITH <%s>
        DELETE { <%s> ?p ?o . }
        WHERE {
            <%s> ?p ?o .
        }""" % (getattr(settings, 'GRAPH_BASE_URL', None), resource_uri, resource_uri)

    _perform_request(query)


def delete_resources_with_predicate(resource_uri, predicate):
    query = """
        WITH <%s>
        DELETE { <%s> <%s> ?o . }
        WHERE {
            <%s> <%s> ?o .
        }""" % (getattr(settings, 'GRAPH_BASE_URL', None), resource_uri, predicate, resource_uri, predicate)

    _perform_request(query)


def update_resource_uri(old_resource_uri, new_resource_uri):
    query = """
        WITH <%s>
        DELETE { ?s ?p <%s> . }
        INSERT { ?s ?p <%s>  .}
        WHERE { ?s ?p <%s> .}
    """ % (getattr(settings, 'GRAPH_BASE_URL', None), old_resource_uri, new_resource_uri, old_resource_uri)

    _perform_request(query)


def empty_graph():
    query = """
        WITH <%s>
        DELETE { ?s ?p ?o . }
        WHERE { ?s ?p ?o . }
    """ % getattr(settings, 'GRAPH_BASE_URL', None)

    _perform_request(query)
