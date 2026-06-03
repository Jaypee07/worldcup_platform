from django.contrib import admin
from .models import Tournament, Team, Group, Match


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'is_active']
    list_editable = ['is_active']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament']
    filter_horizontal = ['teams']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        'home_team', 'away_team', 'stage',
        'status', 'kickoff_time',
        'home_score', 'away_score'
    ]
    list_editable = ['home_score', 'away_score', 'status']
    list_filter = ['stage', 'status', 'tournament']
    search_fields = ['home_team__name', 'away_team__name']
    ordering = ['kickoff_time']