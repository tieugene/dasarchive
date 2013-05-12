#!/usr/bin/env python
# encoding: utf-8
'''
* create Person
* create Another
* create knows P1=>P2

Try to test:
	* rdf_direct/rdf_inverse
	* graph()
	* knows
	* add multiple to rdfDingle
	* apply undescribed attribute
	* ask reverse knows P2=>P1

Add Relationship
Add Organization
try vcard:address, foaf:phone

+ ls all attributes - никак. Хоть foaf_tratata пиши - получишь пустой list()
* ls all available attributes
+ get type of resource (?) - никак. Просто запрашиваешь нужные классы.
+ save to store (load_triples)
+ load from store (just list)
? what if as foaf as vcard?
'''

import rdflib, surf, pprint

def	test01():
	store = surf.Store(reader = "rdflib", writer = "rdflib", rdflib_store = "IOMemory")
	#store = surf.Store(reader = "rdflib", writer = "rdflib", rdflib_store = rdflib.plugin.get('Sleepycat', rdflib.store.Store)('testdb'))
	session = surf.Session(store)
	store.load_triples(source = "card.rdf")
	Person = session.get_class(surf.ns.FOAF.Person)
	all_persons = Person.all()
	Contact = session.get_class(surf.ns.PIM.Contact)
	#all_persons = Contact.all()
	#print "Found %d persons in Tim Berners-Lee's FOAF document" % (len(all_persons))
	for person in all_persons:
		print person
		#pprint.pprint(person.namespaces)
		#print person.foaf_name.first	# first value from list
		#print person.foaf_nick		# rdflib.term.Literal
		#print person.foaf_tratata	# empty list
		#pprint.pprint(person.__dict__)
		#pprint.pprint(person.rdf_direct)	# {...type: [URIRef(foaf/person), URIRef(contact#Male) == rdf_type }
		#pprint.pprint(person.rdf_inverse)	# {}
		#pprint.pprint(person.graph())		# 
		#print person.male_office		# == pim_office; rdflib.term.BNode (blank node => explore graph?
		#print person.contact_office.first.contact_address	# XXX
		#print person.contact_assistant.first	# rdflib.term.URIRef
		#for i in person.rdf_direct:
		#	for j in person.rdf_direct[i]:
		#		#pprint.pprint(surf.util.uri_to_class(j))	# FoafPerson, PimMale
		#		pprint.pprint(surf.util.uri_split(j))		# ('FOAF', u'Person'), ('PIM', u'Male')

def	test00():
	store = surf.Store(reader = "rdflib", writer = "rdflib", rdflib_store = "IOMemory")
	session = surf.Session(store)
	print "Load RDF data"
	store.load_triples(source = "card.rdf")
	Person = session.get_class(surf.ns.FOAF["Person"])	# define class from predefined ns
	all_persons = Person.all()
	print "Found %d persons in Tim Berners-Lee's FOAF document" % (len(all_persons))
	for person in all_persons:
		print person.foaf_name.first

if (__name__ == '__main__'):
	test01()
