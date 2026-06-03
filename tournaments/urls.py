from django.urls import path
from django.views.generic import TemplateView
import tournaments.views as views

app_name = 'tournaments'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('groups/', views.groups_view, name='groups'),
    path('groups/<str:group_name>/', views.group_detail_view, name='group_detail'),
    path('fixtures/', views.fixtures_view, name='fixtures'),
]