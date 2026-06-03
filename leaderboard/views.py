from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaderboardEntry
from payments.models import TournamentTier, Payment


@login_required
def leaderboard_view(request):
    payment = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).first()

    if not payment:
        messages.warning(
            request,
            'You need to join a tier to view the leaderboard.'
        )
        return redirect('payments:tiers')

    tier = payment.tier
    entries = LeaderboardEntry.objects.filter(
        competition=tier.competition
    ).select_related('user').order_by('rank')

    return render(request, 'leaderboard/main.html', {
        'tier_data': [{
            'tier': tier,
            'entries': entries,
        }],
    })