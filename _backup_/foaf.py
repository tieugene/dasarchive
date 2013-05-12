#!/usr/bin/env python
# encoding: utf-8
"""
foaf.py

Created by Philip Cooper on 2007-11-23.
Copyright (c) 2007 Openvest. All rights reserved.
http://api.yandex.ru/blogs/doc/indexation/reference/foaf-standard-tags.xml
"""

from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple
from rdflib import Namespace

FOAF=Namespace("http://xmlns.com/foaf/0.1/" )

class	Agent(rdfSubject):
	# account age tipjar status gender interest holdsAccount topic_interest birthday made mbox_sha1sum
	rdf_type	= FOAF.Agent
	#name		= rdfSingle(FOAF.name)	# диапазон - Thing
	mbox		= rdfMultiple(FOAF.mbox)
	openid		= rdfSingle(FOAF.openid)
	aim		= rdfMultiple(FOAF.aimChatID)
	icq		= rdfMultiple(FOAF.icqChatID)
	msn		= rdfMultiple(FOAF.msnChatID)
	yahoo		= rdfMultiple(FOAF.yahooChatID)
	xmpp		= rdfMultiple(FOAF.jabberID)
	skype		= rdfMultiple(FOAF.skypeID)
	weblog		= rdfMultiple(FOAF.weblog)

class	Person(Agent):
	rdf_type	= FOAF.Person
	first		= rdfSingle(FOAF.firstName)
	last		= rdfSingle(FOAF.surname)
	givenname	= rdfSingle(FOAF.givenname)
	surname		= rdfSingle(FOAF.surname)

class	Organization(Agent):
	rdf_type	= FOAF.Organization

class	Group(Agent):
	rdf_type	= FOAF.Group

class	Document(rdfSubject):
	rdf_type	= FOAF.Document

class	Image(Document):
	rdf_type	= FOAF.Image
