# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class	TagItemInLine(admin.TabularInline):
	model           = TagItem
	extra           = 1

class	FileInLine(admin.TabularInline):
	model           = File
	extra           = 1

# 2. Ordinar
class	TagGroupAdmin(admin.ModelAdmin):
	ordering	= ('name',)
	list_display	= ('name',)
	inlines         = (TagItemInLine,)

class	TagItemAdmin(admin.ModelAdmin):
	ordering	= ('group', 'name')
	list_display	= ('group', 'name')
	#inlines         = (FileInLine,)

class	FileAdmin(admin.ModelAdmin):
	ordering	= ('fname',)
	list_display	= ('pk', 'fname', 'mime', 'size',)
	#inlines         = (TagItemInLine,)
	#include	        = ('mime',)

admin.site.register(TagGroup,	TagGroupAdmin)
admin.site.register(TagItem,	TagItemAdmin)
admin.site.register(File,	FileAdmin)
