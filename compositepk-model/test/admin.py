from django.contrib import admin

from .models import Musician,Album,Company,CompanyBranch

admin.site.register(Musician)
admin.site.register(Album)
admin.site.register(Company)
admin.site.register(CompanyBranch)
