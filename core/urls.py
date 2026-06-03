from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('tournaments.urls')),
    path('predictions/', include('predictions.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('payments/', include('payments.urls')),
]