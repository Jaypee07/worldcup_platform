from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tournament, Group, Match


def home_view(request):
    tournament = Tournament.objects.filter(is_active=True).first()
    return render(request, 'tournaments/home.html', {'tournament': tournament})


def groups_view(request):
    tournament = Tournament.objects.filter(is_active=True).first()
    groups = Group.objects.filter(tournament=tournament).prefetch_related('teams')
    return render(request, 'tournaments/groups.html', {
        'groups': groups,
        'tournament': tournament
    })


def group_detail_view(request, group_name):
    tournament = Tournament.objects.filter(is_active=True).first()
    group = get_object_or_404(Group, name=group_name, tournament=tournament)
    return render(request, 'tournaments/group_detail.html', {'group': group})


def fixtures_view(request):
    tournament = Tournament.objects.filter(is_active=True).first()
    matches = Match.objects.filter(
        tournament=tournament
    ).order_by('kickoff_time').select_related('home_team', 'away_team')
    return render(request, 'tournaments/fixtures.html', {'matches': matches})