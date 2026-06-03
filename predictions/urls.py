from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('group/', views.group_predictions_view, name='group'),
    path('knockout/', views.knockout_predictions_view, name='knockout'),
    path('submit/group/', views.submit_group_prediction, name='submit_group'),
    path('submit/knockout/', views.submit_knockout_prediction, name='submit_knockout'),
    path('my/', views.my_predictions_view, name='my_predictions'),
]