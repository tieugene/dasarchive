#!/usr/bin/env python
# encoding: utf-8

import rdflib, surf, pprint

store = surf.Store(reader = "rdflib", writer = "rdflib", rdflib_store = "IOMemory")
session = surf.Session(store)
store.load_triples(source = "http://www.w3.org/People/Berners-Lee/card.rdf")
Person = session.get_class(surf.ns.FOAF.Person)
all_persons = Person.all()
for person in all_persons:
	print person.foaf_name.first
	pprint.pprint(dir(person))
	pprint.pprint(person.rdf_type)
	pprint.pprint(person.rdf_direct)
	pprint.pprint(person.rdf_inverse)
	#pprint.pprint(person.graph())
	pprint.pprint(dir(person.contact_office))
