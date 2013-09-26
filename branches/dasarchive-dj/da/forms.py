# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe

from models import *

class   FacetForm(forms.ModelForm):
    class   Meta:
        model = Facet

class   TagForm(forms.ModelForm):
    class   Meta:
        model = Tag
