from django.contrib import admin

from .models import Musician,Album,Company,CompanyBranch

admin.site.register(Musician)
admin.site.register(Album)
admin.site.register(Company)

class CompanyBranchAdmin(admin.ModelAdmin):
    list_display = ('company', 'country_code', 'name', 'established_date')

admin.site.register(CompanyBranch, CompanyBranchAdmin)
