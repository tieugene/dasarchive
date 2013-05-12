#!/bin/env python
# -*- coding: utf-8 -*-
'''
Req: python-webpy
Run: 
try: web2py bottle flask pyramid cherripy
'''

# 3rd parties
try:
	import web
except:
	print "install python-webpy first"
try:
	from neo4jrestclient import client
except:
	print "install python-neo4jrestclient first"
# system
import sys, os, tempfile, pprint, datetime

reload(sys)
sys.setdefaultencoding('utf-8')

db = None
debug = True
cache = False
try:
        from local_settings import *
except ImportError:
        pass

render = web.template.render('templates', base='base', cache=cache)

# validators
chk_empty = web.form.Validator('Обязательное поле', bool)

person_form = web.form.Form (
	web.form.Textbox('lastname',	chk_empty, description='Фамилия'),
	web.form.Textbox('firstname',	chk_empty, description='Имя'),
	web.form.Textbox('midname',	description='Отчество'),
)

def	connect():
	global db
	try:
		db = client.GraphDatabase("http://localhost:7474/db/data/")
	except:
		pass

class	Index:
	def	GET(self):
		return render.index()

class	Core:
	def	GET(self):
		return render.core()

class	PersonList:
	def	GET(self):
		global db
		if (db == None):
			connect()
			if db == None:
				print "db err"
		q = 'START n=node(*) RETURN n'
		nodes = db.query(q, returns=(client.Node,))
		return render.person_list(nodes)

class	PersonAdd:
	def	GET(self):
		return render.person_add(person_form())

class	PersonView:
	def	GET(self):
		return render.person_view()

class	PersonEdit:
	def	GET(self):
		return render.person_edit()

class	PersonDel:
	def	GET(self):
		return render.person_del()

urls = (
	'/',			'Index',
	'/core/',		'Core',
	'/person_list/',	'PersonList',
	'/person_add/',		'PersonAdd',
	'/person_view/',	'PersonView',
	'/person_edit/',	'PersonEdit',
	'/person_del/',		'PersonDel',
)

# 1. standalone
if __name__ == '__main__':
	app = web.application(urls, globals())
	app.internalerror = web.debugerror
	app.run()
# 2. apache mod_wsgi
os.chdir(os.path.dirname(__file__))
application = web.application(urls, globals()).wsgifunc()
