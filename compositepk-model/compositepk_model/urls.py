"""
Definition of urls for compositepk_model.
"""

from django.urls import path
from django.contrib import admin
from test import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('musician/', views.MusicianListView.as_view(), name='musician'),
    path('artisit/<int:id>/album/', views.AlbumListView.as_view(), name='album'),
    path('artisit/<int:id>/album/add/', views.AlbumFormView.as_view(), name='add_album'),
    path('company/', views.CompanyListView.as_view(), name='company'),
    path('company/<int:id>/branch/',views.CompanyBranchListView.as_view(), name='companybranch'),
    path('company/<int:id>/branch/add', views.CompanyBranchFormView.as_view(),name='add_companybranch'),
    path('test_filter', views.test_filter,name='test_filter'),
    path('check_keys', views.check_keys,name='check_keys'),
]
