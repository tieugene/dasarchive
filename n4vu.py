#!/bin/env python
# -*- coding: utf-8 -*-
'''
N4vu - Neo4j graph viewer
Req: python-webpy
'''

# 3rd parties
import web, gv
try:
	from neo4jrestclient import client
except:
	print "install python-neo4jrestclient first"
# system
import sys, os, json

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
chk_uint = web.form.regexp('^\d+$', 'Должно быть число')

ptype_list = (('1', 'bool'), ('2', 'int'), ('3', 'str'))

parm_form = web.form.Form (
	web.form.Textbox ('n',	chk_empty, description='Name'),	# not empty; formwide: not exists
	web.form.Dropdown('t',	args=ptype_list, value='3', description='Type'),
	web.form.Textbox ('v', description='Value'),	# formwide: bool: nothing; int: not empty, digit; str: not empty
)

rdir_list = (('1', ' <'), ('2', ' >'))

rel_form = web.form.Form (
	web.form.Dropdown('d',	args=rdir_list, value='1', description='Dir'),
	web.form.Textbox ('t',	chk_empty, description='Type'),		# not empty
	web.form.Textbox ('n',	chk_empty, chk_uint, description='Node'),	# not empty; int; formwide: exists
)

def	getdb():
	global db
	if db == None:
		try:
			db = client.GraphDatabase("http://localhost:7474/db/data/")
		except:
			print "Can't connect db"
			exit()
	return db

class	Index:
	def	GET(self):
		return render.index()

# Nodes
class	NodeList:
	def	GET(self):
		db = getdb()
		return render.node_list(db.query('START n=node(*) RETURN n', returns=(client.Node,)))

class	NodeAdd:
	def	GET(self):
		db = getdb()
		raise web.seeother('/node/%d/' % db.nodes.create().id)

class	NodeView:
	def	GET(self, id):
		db = getdb()
		return render.node_view(db.nodes.get(int(id)), parm_form(), rel_form())

class	NodeDel:
	def	GET(self, id):
		db = getdb()
		db.nodes.get(int(id)).delete()
		raise web.seeother('/node/')

def	chk_parm(item, f):
	'''
	@param f:web.forms.Form
	@return err, name, value
	'''
	err = True
	name = f.n.get_value()
	value = None
	if name in item.properties:
		f.n.note = 'Parameter already exists'
	t = int(f.t.get_value())
	v = f.v.get_value()
	if (t == 1):	# bool
		value = bool(v)
		err = False
	elif (t == 2):	# int
		if v.isdigit():
			value = int(v)
			err = False
		else:
			f.v.note = 'Must be integer'
	else:		# str
		if (v):
			value = v
			err = False
		else:
			f.v.note = 'Must not be empty'
	return err, name, value

# Node parameters
class	NodeParmAdd:
	def	GET(self, id):
		raise web.seeother('/node/%d/' % int(id))
	def	POST(self, id):
		db = getdb()
		node = db.nodes.get(int(id))
		f = parm_form()
		if not f.validates():
			return render.node_view(node, f, rel_form())
		else:
			err, name, value = chk_parm(node, f)
			if (err):
				return render.node_view(node, f, rel_form())
			node[name] = value
			raise web.seeother('/node/%d/' % node.id)

class	NodeParmDel:
	def	GET(self, id, name):
		db = getdb()
		node = db.nodes.get(int(id))
		node.delete(name)
		raise web.seeother('/node/%d/' % node.id)

class	NodeRelDel:
	def	GET(self, id, rel):
		db = getdb()
		db.relationships.get(int(rel)).delete()
		raise web.seeother('/node/%d/' % int(id))

class	NodeRelAdd:
	def	GET(self, id):
		raise web.seeother('/node/%d/' % int(id))
	def	POST(self, id):
		db = getdb()
		node = db.nodes.get(int(id))
		f = rel_form()
		if not f.validates():
			return render.node_view(node, parm_form(), f)
		else:
			#for i in f.inputs: print i.name, f.get(i.name), f.get(i.name).get_value()
			n = db.nodes.get(int(f.n.get_value()), None)
			if not n:
				f.n.note = 'Node not exists'
				return render.node_view(node, parm_form(), f)
			if (int(f.get('d').get_value()) == 1):
				db.relationships.create(n, f.t.get_value(), node)
			else:
				db.relationships.create(node, f.t.get_value(), n)
			raise web.seeother('/node/%d/' % node.id)

# Rel
class	RelView:
	def	GET(self, id):
		db = getdb()
		return render.rel_view(db.relationships.get(int(id)), parm_form())

class	RelDel:
	def	GET(self, id):
		db = getdb()
		db.relationships.get(int(id)).delete()
		raise web.seeother('/node/')

class	RelParmAdd:
	def	GET(self, id):
		raise web.seeother('/rel/%d/' % int(id))
	def	POST(self, id):
		db = getdb()
		rel = db.relationships.get(int(id))
		f = parm_form()
		if not f.validates():
			return render.rel_view(rel, f)
		else:
			err, name, value = chk_parm(rel, f)
			if (err):
				return render.rel_view(rel, f)
			rel[name] = value
			raise web.seeother('/rel/%d/' % rel.id)

class	RelParmDel:
	def	GET(self, id, name):
		db = getdb()
		rel = db.relationships.get(int(id))
		rel.delete(name)
		raise web.seeother('/rel/%d/' % rel.id)

class	Graph:
	def	GET(self):
		db = getdb()
		gdict = dict()
		G = gv.digraph('neo4j')
		gv.setv( G, 'size', '100,100' )
		N = gv.protonode(G)
		gv.setv(N, 'shape', 'rectangle')
		gv.setv(N, 'style', 'rounded')
		for i in db.query('START n=node(*) RETURN n', returns=(client.Node,)):
			id = i[0].id
			gnode = gv.node(G, 'n%d' % id)
			gv.setv(gnode, 'URL', '/node/%d/' % id)
			gdict[id] = gnode
		for i in db.query('START r=relationship(*) RETURN r', returns=(client.Relationship,)):
			edge = i[0]
			gedge = gv.edge(gdict[edge.start.id], gdict[edge.end.id])
			gv.setv(gedge, 'label', edge.type)
			gv.setv(gnode, 'URL', '/rel/%d/' % edge.id)
		gv.layout(G, 'neato')
		svg = gv.renderdata(G, 'svg')
		return render.graph(svg)

class	Export:
	def	GET(self):
		db = getdb()
		dump = list()
		for i in db.query('START n=node(*) RETURN n', returns=(client.Node,)):
			item = i[0]
			d = [0, item.id]
			if item.properties:
				d.append(item.properties)
			dump.append(d)
		for i in db.query('START r=relationship(*) RETURN r', returns=(client.Relationship,)):
			item = i[0]
			d = [1, item.start.id, item.end.id, item.type]
			if item.properties:
				d.append(item.properties)
			dump.append(d)
		web.header('Content-Type', 'application/json')
		web.header('Content-Transfer-Encoding', 'binary')
		web.header('Content-Disposition', 'attachment; filename=\"neo4j.json\";')
		return json.dumps(dump, indent=1)
		#raise web.seeother('/')

class	Import:
	def	GET(self):
		return render.imp()
	def	POST(self):
		db = getdb()
		x = web.input()
		s = x['myfile']
		data = json.loads(s)
		#print data
		nodes = dict()	# map id from file to created nodes
		for i in data:
			if i[0] == 0:	# node
				node = db.nodes.create()
				if len(i) > 2:	# parms
					for k, v in i[2].iteritems():
						node[k] = v
				nodes[i[1]] = node
			else:		# edge
				edge = db.relationships.create(nodes[i[1]], i[3], nodes[i[2]])
				if len(i) > 4:	# parms
					for k, v in i[4].iteritems():
						edge[k] = v
		raise web.seeother('/')

class	Clear:
	def	GET(self):
		db = getdb()
		db.query('START n=node(*) MATCH n-[r?]-() DELETE n,r')	# where id(n)<>0
		db.flush()
		#db.query('START n=node(*) WHERE id(n)<>0 DELETE n')
		raise web.seeother('/')

urls = (
	'/',				'Index',
	'/node/',			'NodeList',
	'/node/add/',			'NodeAdd',
	'/node/(\d+)/',			'NodeView',
	'/node/(\d+)/del/',		'NodeDel',
	'/node/(\d+)/padd/',		'NodeParmAdd',
	'/node/(\d+)/pdel/(.+)',	'NodeParmDel',
	'/node/(\d+)/radd/',		'NodeRelAdd',
	'/node/(\d+)/rdel/(\d+)/',	'NodeRelDel',
	'/rel/(\d+)/',			'RelView',
	'/rel/(\d+)/del/',		'RelDel',
	'/rel/(\d+)/padd/',		'RelParmAdd',
	'/rel/(\d+)/pdel/(.+)',		'RelParmDel',
	'/graph/',			'Graph',
	'/exp/',			'Export',
	'/imp/',			'Import',
	'/cls/',			'Clear',
)

# 1. standalone
if __name__ == '__main__':
	app = web.application(urls, globals())
	app.internalerror = web.debugerror
	app.run()
# 2. apache mod_wsgi
os.chdir(os.path.dirname(__file__))
application = web.application(urls, globals()).wsgifunc()
