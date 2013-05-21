#!/bin/env python
# -*- coding: utf-8 -*-
'''
'''

# 1. 3rd parties
# - flask
import flask
from flask.ext.wtf import Form, TextField, DateField, SelectField, Required, FileField
#from flask.ext.wtf.html5 import DateField
from werkzeug import secure_filename
# - graph
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from bulbs.neo4jserver import Graph
# from neo4jrestclient import client
# - graphviz
import gv
# 2. my
import utils
# 3. system
import sys, os, collections, pprint, StringIO, json, datetime
# 4. const

DEBUG = True
CSRF_ENABLED = False
SECRET_KEY = 'tratata'
INBOX_ROOT = '/mnt/shares/ftp/pub'
OUTBOX_ROOT = '/mnt/shares/tmp/da'

# 5. local
try:
        from local_settings import *
except ImportError:
        pass

app = flask.Flask(__name__)
app.config.from_object(__name__)

class	TagNodeModel(Node):
    element_type = 'tag'
    name    = String(nullable=False)

class	FacetNodeModel(Node):
    element_type = 'facet'	# predefined key 'element_type':str
    name    = String(nullable=False)

class	FileNodeModel(Node):
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

class	TagNodeForm(Form):
    name	= TextField('Наименование', validators=[Required()])

class	FacetNodeForm(Form):
    name	= TextField('Наименование', validators=[Required()])

class	FileNodeForm(Form):
    name	= TextField('Наименование', validators=[Required()])
    fname	= TextField('Имя файла', validators=[Required()])
    comment	= TextField('Комментарии')
    mime	= TextField('Mime')

class	TagsImportForm(Form):
    name	= FileField('File', validators=[Required()])

class	FileUploadForm(Form):
    name	= FileField('File', validators=[Required()])

g = Graph()
g.add_proxy('tags',     TagNodeModel)
g.add_proxy('facets',   FacetNodeModel)
g.add_proxy('files',    FileNodeModel)

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

@app.route('/tagmap/')
def tagmap():
    gdict = dict()
    G = gv.digraph('dasarchive')
    gv.setv( G, 'size', '100,100' )
    N = gv.protonode(G)
    gv.setv(N, 'shape', 'rectangle')
    gv.setv(N, 'style', 'rounded,filled')
    gv.setv(N, 'fillcolor', '#F0F0F0')
    gv.setv(N, 'width', '0')
    gv.setv(N, 'height', '0')
    gv.setv(N, 'margin', '0.05,0.025')
    for node in g.V:
        gnode = gv.node(G, 'n%d' % node.eid)
        gv.setv(gnode, 'URL', '/tag/%d/' % node.eid)
        if (node.eid):  # not root
            gv.setv(gnode, 'label', node.name.encode('utf8'))
            if (node.element_type == 'facet'):
                gv.setv(gnode, 'fillcolor', 'lightgreen')
        else:
            gv.setv(gnode, 'label', '/')
            gv.setv(gnode, 'fillcolor', 'silver')
        gdict[node.eid] = gnode
    for node in g.V:
        if node.outV():
            for out in node.outV():
                gedge = gv.edge(gdict[node.eid], gdict[out.eid])
    gv.layout(G, 'neato')
    svg = gv.renderdata(G, 'svg')
    return flask.render_template('tag_map.html', svg=svg)

#app.route('/tag/')
@app.route('/tag/<int:tag_id>/')
def tag(tag_id=0):
    '''
    Retrieve all linked tags and facets - as parent as sub.
    @param tag_id - tag id to retrieve
    '''
    #g.files.get_all()
    tag = g.vertices.get(tag_id)
    return flask.render_template('tag_index.html', tag=tag)

@app.route('/tag/<int:tag_id>/addtag/', methods=['GET', 'POST'])
def tag_add_tag(tag_id):
    '''
    Add new subtag to given tag/facet.
    '''
    parent = g.vertices.get(tag_id)
    form = TagNodeForm()
    if form.validate_on_submit():
        child = g.tags.create(name=form.name.data)
        g.edges.create(parent, 'tag', child)
        return flask.redirect(flask.url_for('tag', tag_id=tag_id))
    return flask.render_template('tag_form.html', form=form, tag=parent)

@app.route('/tag/<int:tag_id>/addfacet/', methods=['GET', 'POST'])
def tag_add_facet(tag_id):
    '''
    Add new facet to given tag.
    '''
    parent = g.vertices.get(tag_id)
    form = FacetNodeForm()
    if form.validate_on_submit():
        child = g.facets.create(name=form.name.data)
        g.edges.create(parent, 'facet', child)
        return flask.redirect(flask.url_for('tag', tag_id=tag_id))
    return flask.render_template('tag_form.html', form=form, tag=parent)

@app.route('/tag/<int:tag_id>/edit/', methods=['GET', 'POST'])
def tag_edit(tag_id):
	tag = g.vertices.get(tag_id)
	form = TagNodeForm()
	if flask.request.method == 'POST':
		if form.validate_on_submit():
			tag.name = form.name.data
			tag.save()
			return flask.redirect(flask.url_for('tag', tag_id=tag_id))
	else:
		form.name.data = tag.name
	return flask.render_template('tag_form.html', form=form, tag=tag)

@app.route('/tag/<int:tag_id>/del/')
def tag_del(tag_id):
    tag = g.vertices.get(tag_id)
    if (tag.outV()):
        return flask.redirect(flask.url_for('tag_del_err', tag_id=tag_id))
    ins = tag.inE()
    if ins:
        parent = tag.inV().next()
        for edge in ins:
            g.edges.delete(edge.eid)
    else:
        parent = g.vertices.get(0)
    g.vertices.delete(tag_id)
    return flask.redirect(flask.url_for('tag', tag_id=parent.eid))

@app.route('/tag/<int:tag_id>/delerr/')
def tag_del_err(tag_id):
    return flask.render_template('tag_del_err.html', tag=g.vertices.get(tag_id))

@app.route('/file/')
def file():
	files = g.files.get_all()
	return flask.render_template('file_list.html', files=files if files else [])

@app.route('/file/upload/', methods=['GET', 'POST'])
def file_upload():
    '''
    name    = String(nullable=False)
    fname   = String(nullable=False)
    comment = String()
    mime    = String()                  form.name.data.mimetype
    size    = Integer(nullable=False)   form.name.data.content_length - err
    md5     = String()
    ctime   = DateTime(nullable=False)
    mtime   = DateTime(nullable=False)
    updated = DateTime(nullable=False)
    '''
    form = FileUploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.name.data.filename)
        # 1. create node
        now = datetime.datetime.now()
        gfile = g.files.create(
            name=filename,
            fname=filename,
            mime=str(form.name.data.mimetype),
            size=form.name.data.content_length,
            ctime=now,
            mtime=now,
            updated=now
        )
        # 2. save file
        form.name.data.save(os.path.join(OUTBOX_ROOT, '%08X' % gfile.eid))
        form.name.data.close()
        # 3. post-save actions: size, md5
        # X. the end
        return flask.redirect(flask.url_for('file'))    # FIXME: file_view
    else:
        filename = None
    return flask.render_template('file_upload_form.html', form=form, filename=filename)

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

@app.route('/export/')
def tags_export():
    dump = list()
    # 1. nodes
    for node in g.V:
        d = [0, node.eid]
        if node.data():
            d.append(node.data())
        dump.append(d)
    # 2. edges
    for edge in g.E:
        d = [1, edge.outV().eid, edge.inV().eid, edge.label()]
        if edge.data():
            d.append(edge.data())
        dump.append(d)
    # 3. convert
    #return flask.jsonify(dump)
    return flask.send_file(StringIO.StringIO(json.dumps(dump, indent=1)), mimetype='application/json', as_attachment=True, attachment_filename='dasarchive.json')

@app.route('/clean/')
def tags_clean():
    if (g.E):
        for edge in g.E:
            g.edges.delete(edge.eid)
    for node in g.V:
        if (node.eid):
            g.vertices.delete(node.eid)
    return flask.redirect(flask.url_for('index'))

@app.route('/import/', methods=('GET', 'POST'))
def tags_import():
    form = TagsImportForm()
    if form.validate_on_submit():
        data = json.loads(form.name.data.read())
        nodes = {0: g.vertices.get(0)}	# map node id from file to created ones
        for i in data:
            if (i[0] == 0):	    # node
                if (i[1] != 0): # skip root!
                    node = g.vertices.create(element_type=i[2]['element_type'], name=i[2]['name'])
                    #if len(i) > 2:	# parms
                    #    for k, v in i[2].iteritems():
                    #        node[k] = v
                    nodes[i[1]] = node
            else:		        # edge
                edge = g.edges.create(nodes[i[1]], i[3], nodes[i[2]])
                #if len(i) > 4:	# parms
                #	for k, v in i[4].iteritems():
                #		edge[k] = v
        return flask.redirect(flask.url_for('index'))
    else:
        filename = None
    return flask.render_template('import_form.html', form=form, filename=filename)

# Go
# - standalone
if __name__ == '__main__':
    app.run()
