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
	person.load()
	l = list()
	for key in person.rdf_direct:
		l.append(surf.util.rdf2attr(key, True))
		#print attr
		#pprint.pprint(person[attr])
		#if (attr == 'pim_office'):
		#	print 'pim_office catched!'
		#	a = person.pim_office
		#	a.load()
		#	pprint.pprint(a)
	l.sort()
	pprint.pprint(l)
	pprint.pprint(dir(person.pim_office))
