"""
Definition of models.
"""

from django.db import models

# Create your models here.
# Test For CPkModel
from cpkmodel import *


# Normal Model
#   primary_key is auto 'id'
class Company(models.Model):
    name = models.CharField(max_length=100)
    established_date = models.DateField()
    company_code = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Company'

# Child Model (CpkModel)
#   primary_key is composite-key: company_id, country_code
class CompanyBranch(CPkModel):
    company = models.ForeignKey(
        Company,
        primary_key=True,       # for CompositePK
        on_delete=models.CASCADE)
    country_code = models.CharField(
        max_length=100,
        primary_key=True,       # for CompositePK
    )
    name = models.CharField(max_length=100)
    established_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'CompanyBranch'
        unique_together = (('company', 'country_code'),)


# CpkModel with single primary key
#   primary_key is auto 'id'
class Musician(CPkModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Musician'


# Child Model (CpkModel)
#   primary_key is composite-key: artist_id, album_no
class Album(CPkModel):
    artist = models.ForeignKey(
        Musician,
        primary_key=True,       # for CompositePK
        on_delete=models.CASCADE)
    album_no = models.IntegerField(
        primary_key=True,       # for CompositePK
    )
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
    item_code = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'Album'
        unique_together = (('artist', 'album_no'),)
