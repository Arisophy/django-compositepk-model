"""
Definition of forms.
"""

from django import forms
from django.forms.widgets import DateInput
from .models import Company

class AlbumForm(forms.Form):

    name = forms.CharField(
        label="name",
        max_length=100,
    )
    release_date = forms.DateField(
        label='release_date',
        widget=DateInput(),
    )
    num_stars = forms.IntegerField(
        label='num_stars',
        min_value=0,
        max_value=5,
    )
    item_code = forms.CharField(
        label="item_code",
        max_length=100,
    )
    company = forms.ModelChoiceField(
        label='company',
        queryset=Company.objects.all()
    )

class CompanyBranchForm(forms.Form):

    country_code = forms.CharField(
        label="country_code",
        max_length=100,
    )
    name = forms.CharField(
        label="name",
        max_length=100,
    )
    established_date = forms.DateField(
        label='established_date',
        widget=DateInput(),
    )
