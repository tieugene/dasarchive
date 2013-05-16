#!/bin/env python
# -*- coding: utf-8 -*-
'''
Req: python-flask, python-bulbs
Relationships:
* Inherit (Person > Patient)
* Is (Person > gender)
* Has (Person > document)
'''

# 1. 3rd parties
# - flask
import flask
from flask.ext.wtf import Form, TextField, DateField, SelectField, Required
#from flask.ext.wtf.html5 import DateField
# - graph
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.neo4jserver import Graph
# from neo4jrestclient import client
# 2. my
# 3. system
import sys, os
# 4. local
try:
        from local_settings import *
except ImportError:
        pass

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'tratata'

class	PersonModel(Node):
	element_type = 'person'	# predefined key 'element_type':str
	lastname = String(nullable=False)
	firstname = String(nullable=False)
	midname = String()
	#gender == link
	# birthdate - DateTime only => need implement
	birthplace = String()

#class	Knows(Relationship):
#	label = "knows"

class	PersonForm(Form):
	lastname	= TextField('Фамилия', validators=[Required()])
	firstname	= TextField('Имя', validators=[Required()])
	midname		= TextField('Отчество')
	gender		= SelectField('Секас', choices=[('1', 'муж'), ('2', 'жен')])
	#birthdate	= DateField('Дата рождения', format='%d/%m/%y') - required by default - due format err
	birthplace	= TextField('Место рождения')

app = flask.Flask(__name__)
app.config.from_object(__name__)

g = Graph()
g.add_proxy('persons', PersonModel)

reload(sys)
sys.setdefaultencoding('utf-8')

@app.route('/')
def index():
    return flask.render_template('index.html')
 
@app.route('/registry/')
def registry():
    return flask.render_template('registry_index.html')
 
@app.route('/patient/')
def patient():
    return flask.render_template('patient_list.html')
 
@app.route('/employee/')
def employee():
    return flask.render_template('employee_index.html')
 
@app.route('/service/')
def service():
    return flask.render_template('service_index.html')

@app.route('/person/')
def person():
	persons = g.persons.get_all()
	return flask.render_template('person_list.html', persons=persons if persons else [])

@app.route('/person/add/', methods=['GET', 'POST'])
def person_add():
	form = PersonForm()
	if form.validate_on_submit():
		person = g.persons.create(lastname=form.lastname.data, firstname=form.firstname.data)
		return flask.redirect(flask.url_for('person_view', item_id=person.eid))
	return flask.render_template('person_form.html', form=form)

@app.route('/person/<int:item_id>/')
def person_view(item_id):
	return flask.render_template('person_view.html', person=g.persons.get(int(item_id)))
 
@app.route('/person/<int:item_id>/del/')
def person_del(item_id):
	g.persons.delete(int(item_id))
	return flask.redirect(flask.url_for('person'))
 
@app.route('/person/<int:item_id>/edit/', methods=['POST', 'GET'])
def person_edit(item_id):
	item=g.persons.get(int(item_id))
	form = PersonForm()
	if flask.request.method == 'POST':
		if form.validate_on_submit():
			item.lastname=form.lastname.data
			item.firstname=form.firstname.data
			item.save()
			return flask.redirect(flask.url_for('person_view', item_id=item.eid))
	else:
		form.lastname.data = item.lastname
		form.firstname.data = item.firstname
	return flask.render_template('person_form.html', form=form)

# Go
# - standalone
if __name__ == '__main__':
    app.run()
