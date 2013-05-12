# -*- coding: utf-8 -*-
'''
forms.py
'''

from django import forms
from django.utils.datastructures import SortedDict

import sys, pprint

from models import *

reload(sys)
sys.setdefaultencoding('utf-8')

FilterFormTags = None

class FilterFormMain(forms.Form):
        contains = forms.CharField(label='Содержит', required = False)
        deleted = forms.ChoiceField(
                choices=((1, 'Не скрытые'), (2, 'Скрытые'), (3, 'Все')),
                label='Показывать',
            )
        concat = forms.ChoiceField(
                choices=((1, 'ИЛИ'), (2, 'И'), (3, 'ИЛИ строго'), (4, 'И строго')),
                label='Теги по',
            )

def set_filter():
    '''
    Create tags form for FileList filter - as set of CheckboxSelectMultiple named as tags-tag<taggroup.pk>
    '''
    global FilterFormTags
    if (FilterFormTags == None):
        fields = SortedDict()
        for tag_group in TagGroup.objects.all():
            field = forms.MultipleChoiceField(
                choices=[(s.pk, s.name) for s in tag_group.items.all()],
                widget=forms.CheckboxSelectMultiple,
                label=tag_group.name,
                required = False,
            )
            fields['tag%d' % tag_group.pk] = field
        FilterFormTags = type('FilterFormTags', (forms.BaseForm,), {'base_fields': fields})
    return FilterFormTags

class   FileForm(forms.ModelForm):
    '''
    Form for filelist filter
    '''
    tags = forms.ModelMultipleChoiceField(queryset=TagItem.objects, widget=forms.CheckboxSelectMultiple())  #, required=False)

    class   Meta:
        model = File
        widgets = {
        #    'tags': forms.CheckboxSelectMultiple(),
            'comment': forms.Textarea(),
        }
        #fields = ('file',)
        exclude = ('mime',)
