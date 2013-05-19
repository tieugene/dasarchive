#!/bin/env python
# -*- coding: utf-8 -*-
'''
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
import utils
# 3. system
import sys, os, collections
# 4. const

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'tratata'
INBOX_ROOT = '/mnt/shares/ftp/pub'

# 5. local
try:
        from local_settings import *
except ImportError:
        pass

class	FacetModel(Node):
    element_type = 'facet'	# predefined key 'element_type':str

class	TagModel(Node):
    element_type = 'tag'

class	FileModel(Node):
    element_type = 'file'
    name    = String(nullable=False)
    fname   = String(nullable=False)
    comment = String()
    mime    = String()
    size    = Integer(nullable=False)
    md5     = String()
    ctime   = DateTime(nullable=False)
    mtime   = DateTime(nullable=False)
    updated = DateTime(nullable=False)
    #deleted = models.BooleanField(default=False, editable=False, verbose_name=u'Удален')

class	FileForm(Form):
    name	= TextField('Наименование', validators=[Required()])
    fname	= TextField('Имя файла', validators=[Required()])
    comment	= TextField('Комментарии')
    mime	= TextField('Mime')

app = flask.Flask(__name__)
app.config.from_object(__name__)

g = Graph()
g.add_proxy('facets', FacetModel)
g.add_proxy('tags', TagModel)
g.add_proxy('file', FileModel)

reload(sys)
sys.setdefaultencoding('utf-8')

@app.route('/')
def index():
    return flask.render_template('index.html')

def pathurls(path):
    '''
    '''
    pathlist = path.split('/')
    retlist = list()
    for i, p in enumerate(pathlist[:-1]):
        retlist.append(u'<a href="%s"> <button type="button"> %s </button> </a>' % (url_for('inbox', args=['/'.join(pathlist[:i+1])]), p))
    return retlist+pathlist[-1:]

@app.route('/inbox/')
@app.route('/inbox/<path>')
def inbox(path=''):
    fullpath = os.path.join(INBOX_ROOT, path).encode('utf-8')
    if (os.path.isdir(fullpath)):
        for (p, d, f) in os.walk(fullpath):
            break
        d.sort()
        f.sort()
        files = collections.OrderedDict()
        for isdir, df in ((True, d), (False, f)):
            for i in df:
                stat = os.stat(os.path.join(fullpath, i))
                files[i] = {
                    'isdir':    isdir,
                    'name':     i,
                    'path':     os.path.join(path, i),
                    'size':     stat.st_size,
                    #'mtime':    datetime.datetime.fromtimestamp(stat.st_mtime),
                    #'ctime':    datetime.datetime.fromtimestamp(stat.st_ctime),
                }
        #for k, v in files.iteritems()
        #files = os.listdir(path)
        return flask.render_template('inbox_index.html', pathurls=pathurls(path), data=files, path=path)
        #return flask.render_template('inbox_index.html', data=files, path=path)
    else:
        response = HttpResponse(content_type = utils.get_mime(fullpath))
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = (u'attachment; filename=\"%s\";' % os.path.basename(fullpath)).encode('utf-8')
        response.write(open(fullpath).read())
        return response

@app.route('/tag/')
def tag():
    return flask.render_template('tag_list.html')

@app.route('/file/')
def file():
	files = g.files.get_all()
	return flask.render_template('file_list.html', files=files if files else [])

@app.route('/file/add/<path>', methods=['GET', 'POST'])
def file_add(path):
	form = PersonForm()
	if form.validate_on_submit():
		file = g.files.create(lastname=form.lastname.data, firstname=form.firstname.data)
		return flask.redirect(flask.url_for('file_view', item_id=file.eid))
	return flask.render_template('file_form.html', form=form)

@app.route('/file/<int:item_id>/')
def file_view(item_id):
	return flask.render_template('file_view.html', file=g.files.get(int(item_id)))

@app.route('/file/<int:item_id>/del/')
def file_del(item_id):
	g.files.delete(int(item_id))
	return flask.redirect(flask.url_for('file'))

@app.route('/file/<int:item_id>/edit/', methods=['POST', 'GET'])
def file_edit(item_id):
	item=g.files.get(int(item_id))
	form = PersonForm()
	if flask.request.method == 'POST':
		if form.validate_on_submit():
			item.lastname=form.lastname.data
			item.firstname=form.firstname.data
			item.save()
			return flask.redirect(flask.url_for('file_view', item_id=item.eid))
	else:
		form.lastname.data = item.lastname
		form.firstname.data = item.firstname
	return flask.render_template('file_form.html', form=form)

# Go
# - standalone
if __name__ == '__main__':
    app.run()
