# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

class	NodeAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	#list_display	= ('id', 'user', 'type', 'name', 'created', 'updated')

class	FacetAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	#list_display	= ('id', 'user', 'type', 'name', 'created', 'updated')

class	TagAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	#list_display	= ('id', 'user', 'type', 'name', 'created', 'updated')


admin.site.register(Node,	NodeAdmin)
admin.site.register(Facet,	FacetAdmin)
admin.site.register(Tag,	TagAdmin)
