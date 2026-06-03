from django.contrib import admin
from .models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'total_points', 'rank']
    list_filter = ['competition']
    ordering = ['rank']