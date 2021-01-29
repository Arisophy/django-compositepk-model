"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.db.models import Max
from django.db import DatabaseError, InterfaceError
from test.models import (
    Musician,
    Album,
    Company,
    CompanyBranch,
)
from test.forms import (
    AlbumForm,
    CompanyBranchForm,
)


################
# home
################
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
    )

################
# Musician
################
class MusicianListView(ListView):
    template_name = 'app/musician.html'
    model = Musician


################
# Album
################
class AlbumListView(ListView):
    template_name = 'app/album.html'
    model = Album

    def get_queryset(self):
        artist_id = self.kwargs['id']
        ######################################
        # filter pattern(1) : id=val
        musician = Musician.objects.get(id=artist_id)
        ######################################
        # filter pattern(2) : artist=obj
        return super().get_queryset().filter(artist=musician)


class AlbumFormView(FormView):
    template_name = 'app/album_create.html'
    form_class = AlbumForm

    def get_context_data(self, **kwargs):
        objects = [] 
        artist_id = self.kwargs['id']
        ######################################
        # filter pattern(3) : pk=val
        musician = Musician.objects.get(pk=artist_id)
        objects.append(
            {'key':" Musician.objects.get(pk=%s)" % artist_id, 'val':musician}
        )
        ######################################
        # filter pattern(4) : artist__in=[obj,]
        vals  = [musician,]
        album_max_no = Album.objects.filter(artist__in=vals).aggregate(Max('album_no'))
        objects.append(
            {'key':"Album.objects.filter(artist__in=%s).aggregate(Max('album_no'))" % vals, 'val':album_max_no}
        )
        context = {
            'objects':objects,
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_success_url(self):
        return "/artisit/%s/album/" % self.kwargs['id']

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        artist_id = self.kwargs['id']
        ######################################
        # filter pattern(5) : id__in=[val,]
        vals = [artist_id,]
        musician = Musician.objects.filter(id__in=vals)[0]
        cleaned_data['artist'] = musician
        ######################################
        # filter pattern(6) : artist_id=musician.id
        album_max_no = Album.objects.filter(artist_id=musician.id).aggregate(Max('album_no')).get('album_no__max')
        album_next_no = int(album_max_no) + 1 if album_max_no else 1
        cleaned_data['album_no'] = album_next_no
        ######################################
        # Create pattern(1) : By Model.save
        album = Album(**cleaned_data)
        album.save()
        return super().form_valid(form)


################
# Company
################
class CompanyListView(ListView):
    template_name = 'app/company.html'
    model = Company


################
# CompanyBranch
################
class CompanyBranchListView(ListView):
    template_name = 'app/company_branch.html'
    model = CompanyBranch

    def get_queryset(self):
        company_id = self.kwargs['id']
        company = Company.objects.get(pk=company_id)
        return super().get_queryset().filter(company=company)


class CompanyBranchFormView(FormView):
    template_name = 'app/company_branch_create.html'
    form_class = CompanyBranchForm

    def get_context_data(self, **kwargs):
        objects = [] 
        company_id = self.kwargs['id']
        ######################################
        # filter pattern(7) : pk__in=[val,]
        vals = [company_id,]
        company = Company.objects.filter(pk__in=vals)[0]
        objects.append(
            {'key':"  Company.objects.filter(pk__in=%s)[0]" % vals, 'val':company}
        )
        context = {
            'objects':objects,
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_success_url(self):
        return "/company/%s/branch/" % self.kwargs['id']

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        company_id = self.kwargs['id']
        ######################################
        # filter pattern(8) : id__in=(val,)
        vals = (company_id,)
        company = Company.objects.filter(id__in=vals)[0]
        cleaned_data['company'] = company
        ######################################
        # Create pattern(2) : By QuerySet.create
        branch = CompanyBranch.objects.create(**cleaned_data)
        return super().form_valid(form)


################
# test_filter
################
def test_filter(request):
    def exec_test(no, key, val, memo):
        result = None
        try:
            result = Album.objects.filter(**{key:val})
            print(result)
        except Exception as e:
            result = e
        
        return {'no':no, 'key':key, 'val':val, 'result':result, 'memo':memo}

    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    musician = Musician.objects.first()
    album = Album.objects.first()
    company = Company.objects.last()
    qs_kv_name_startwith = Album.objects.filter(name__startswith='N').values('artist', 'album_no')
    #qs_kv_name_startwith = Album.objects.filter(name__startswith='N')
    SQLite_error = "##[SQLite]NG, [PostgreSQL]OK"
    test_data = (
        (1, 'artist', musician, ""),
        (2, 'artist', musician.id, ""),
        (3, 'artist_id', musician.id, ""),
        (11, 'pk', (musician.id, 1), ""),
        (13, 'artist,album_no', (musician, 1), ""),
        (14, 'artist,album_no', (musician.id, 1), ""),
        (15, 'artist_id,album_no', (musician.id, 1), ""),
        (21, 'num_stars', 5, ""),
        (31, 'name', "David Bowie", ""),
        (32, 'name__startswith', "N", ""),
        (91, 'pk', musician.id, "## Param Error ##"),
        # relation model
        (101, 'artist__id', musician.id, ""),
        (102, 'artist__profile__contains', "Rock", ""),
        (111, 'artist__id,first_name', (1,'Michael'), ""),
        (121, 'company__company_code', 'SME', ""),
        (122, 'company__company_code__startswith', 'S', ""),
        (123, 'company__company_code__in', ['SME','WB'], ""),
        (131, 'company__companybranch__country_code', 'JP', ""),
        (132, 'company__companybranch__country_code__startswith', 'U', ""),
        (191, 'artist__pk', musician.id, "## Not Supported ##"),
        # __in
        (201, 'pk__in', [(musician.id, 1)], SQLite_error),
        (202, 'pk__in', [(1, 1),(2,1)],SQLite_error),
        (203, 'pk__in', ['1,1','2,1'], SQLite_error),
        (204, 'pk__in', qs_kv_name_startwith, SQLite_error),
        (205, 'pk__in', list(qs_kv_name_startwith), SQLite_error),
        (211, 'artist_id,album_no__in', [(1, 1),(2,1)], SQLite_error),
        (212, 'artist,album_no__in', [(1, 1),(1,2)], SQLite_error),
        (221, 'artist,album_no__in', qs_kv_name_startwith, SQLite_error),
        (222, 'artist_id,album_no__in', qs_kv_name_startwith, SQLite_error),
        (231, 'num_stars__in', [4,5], ""),
        (232, 'album_no__in', [1], ""),
        # relation + __in
        (301, 'artist__pk__in', [1,2], ""),
        (302, 'artist__id__in', [1,2,3], ""),
        (311, 'company__pk__in', [1,2,3,4], ""),
        (312, 'company__id__in', [2,3,4], ""),
        (321, 'company__companybranch__company_id,country_code', (1,'JP'), ""),
        # Not Supported
        (901, 'company__companybranch__company_id,country_code__in', [(1,'JP'),(2,'JP')], "## Not Supported ##"),
        (911, 'name,item_code__contains', ('Mic','TEST'), "## Not Supported ##"),
    )

    objects = tuple(exec_test(no,key,val,memo) for no,key,val,memo in  test_data)

    return render(
        request,
        'app/test_filter.html',
        {
            'objects':objects,
        },
    )


################
# check_keys
################
def check_keys(request):
    def make_result(name, obj):
        col = obj._meta.pk.get_col(name)
        result = {
            'name':name,
            'meta':obj._meta,
            'pk':obj._meta.pk,
            'pk_cls':obj._meta.pk.__class__.__name__,
            'col':col,
        }
        return result

    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    musician = Musician.objects.first()
    album = Album.objects.first()
    company = Company.objects.first()
    branch = CompanyBranch.objects.first()
    
    objects = [
        make_result('Musician', musician),
        make_result('Company', company),
        make_result('Album', album),
        make_result('CompanyBranch', branch),
    ]
    return render(
        request,
        'app/check_keys.html',
        {
            'objects':objects,
        }
    )
