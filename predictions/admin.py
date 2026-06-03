from django.contrib import admin
from .models import Competition, Prediction


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'match', 'competition',
        'predicted_home_score', 'predicted_away_score',
        'predicted_winner', 'points_awarded', 'is_scored'
    ]
    list_filter = ['competition', 'is_scored']
    search_fields = ['user__username']