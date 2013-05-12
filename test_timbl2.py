#!/usr/bin/env python
# encoding: utf-8

import rdflib, surf, pprint

store = surf.Store(reader = "rdflib", writer = "rdflib", rdflib_store = "IOMemory")
session = surf.Session(store)
store.load_triples(source = "http://www.w3.org/People/Berners-Lee/card.rdf")
Person = session.get_class(surf.ns.FOAF.Person)
person = Person.all().first()
print person.foaf_name.first
person.load()
#pprint.pprint(dir(person))
pprint.pprint(person.pim_office)
person.pim_office.load()