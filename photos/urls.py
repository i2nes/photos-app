from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.PhotoListView.as_view(), name='photo_list'),
    path('photo/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photo/<int:pk>/thumbnail/', views.photo_thumbnail, name='photo_thumbnail'),
    path('photo/<int:pk>/full/', views.photo_full, name='photo_full'),
    path('stats/', views.stats_view, name='stats'),
    path('api/search/', views.search_autocomplete, name='search_autocomplete'),
]