# -*- coding: utf-8 -*-
'''
lansite.apps.task.forms.py
'''

from django import forms
from django.utils.datastructures import SortedDict

import sys, pprint

from models import *

reload(sys)
sys.setdefaultencoding('utf-8')

FilterForm = None

def	set_filter():
	global FilterForm
	if (FilterForm == None):
		fields = SortedDict()
		fields['concat'] = forms.ChoiceField(
				choices=((1, 'Или'), (2, 'И минимум'), (3, 'И строго')),
				label='Фильтр по',
			)
		fields['deleted'] = forms.ChoiceField(
				choices=((1, 'Живые'), (2, 'Удаленные'), (3, 'Все')),
				label='Удаленные',
			)
		for tag_group in TagGroup.objects.all():
			fields['tag%d' % tag_group.pk] = forms.MultipleChoiceField(
				choices=[(s.pk, s.name) for s in tag_group.items.all()],
				widget=forms.CheckboxSelectMultiple,
				label=tag_group.name,
				required = False,
			)
		FilterForm = type('FilterForm', (forms.BaseForm,), {'base_fields': fields})
	return FilterForm

class	FileForm(forms.ModelForm):
	'''
	Form for filelist filter
	'''
	tags = forms.ModelMultipleChoiceField(queryset=TagItem.objects, widget=forms.CheckboxSelectMultiple(), required=False)

	class	Meta:
		model = File
		#fields = ('file',)
