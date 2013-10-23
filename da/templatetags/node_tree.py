# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag('node/tree.html', takes_context=True)
def node_tree(context, node):
    return {'node': node}

@register.inclusion_tag('file/tag_tree.html', takes_context=True)
def tags_tree(context, node, object):
    return {'node': node, 'object': object}
