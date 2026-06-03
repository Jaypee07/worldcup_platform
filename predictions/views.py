from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Competition, Prediction
from tournaments.models import Match, Tournament, Team


@login_required
def group_predictions_view(request):
    from payments.models import Payment

    tournament = Tournament.objects.filter(is_active=True).first()

    payment = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).first()

    if not payment:
        messages.warning(
            request,
            'You need to join a tier before making predictions.'
        )
        return redirect('payments:tiers')

    competition = payment.tier.competition

    matches = Match.objects.filter(
    tournament=tournament,
    stage=Match.Stage.GROUP,
    status=Match.Status.UPCOMING
).select_related('home_team', 'away_team').order_by('kickoff_time')

    pred_map = {}
    for p in Prediction.objects.filter(
        user=request.user,
        competition=competition,
        match__stage=Match.Stage.GROUP
    ).select_related('match'):
        pred_map[p.match.id] = {
            'home': p.predicted_home_score,
            'away': p.predicted_away_score,
        }

    return render(request, 'predictions/group.html', {
        'matches': matches,
        'pred_map': pred_map,
        'competition': competition,
    })


@login_required
def submit_group_prediction(request):
    if request.method != 'POST':
        return redirect('predictions:group')

    competition_id = request.POST.get('competition_id')
    competition = get_object_or_404(Competition, id=competition_id)

    match_ids = request.POST.getlist('match_id')

    for match_id in match_ids:
        match = get_object_or_404(Match, id=match_id)

        if match.status != Match.Status.UPCOMING:
            continue

        home_score = request.POST.get(f'home_{match_id}')
        away_score = request.POST.get(f'away_{match_id}')

        if home_score == '' or away_score == '':
            continue

        Prediction.objects.update_or_create(
            user=request.user,
            match=match,
            competition=competition,
            defaults={
                'predicted_home_score': int(home_score),
                'predicted_away_score': int(away_score),
            }
        )

    messages.success(request, 'Predictions saved.')
    return redirect('predictions:group')


@login_required
def knockout_predictions_view(request):
    from payments.models import Payment

    tournament = Tournament.objects.filter(is_active=True).first()

    payment = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).first()

    if not payment:
        messages.warning(
            request,
            'You need to join a tier before making predictions.'
        )
        return redirect('payments:tiers')

    competition = payment.tier.competition

    matches = Match.objects.filter(
        tournament=tournament,
        status=Match.Status.UPCOMING
    ).exclude(stage=Match.Stage.GROUP).select_related('home_team', 'away_team')

    return render(request, 'predictions/knockout.html', {
        'matches': matches,
        'competition': competition,
    })


@login_required
def submit_knockout_prediction(request):
    if request.method != 'POST':
        return redirect('predictions:knockout')

    competition_id = request.POST.get('competition_id')
    competition = get_object_or_404(Competition, id=competition_id)

    match_ids = request.POST.getlist('match_id')

    for match_id in match_ids:
        match = get_object_or_404(Match, id=match_id)

        if match.status != Match.Status.UPCOMING:
            continue

        winner_id = request.POST.get(f'winner_{match_id}')
        if not winner_id:
            continue

        winner = get_object_or_404(Team, id=winner_id)

        Prediction.objects.update_or_create(
            user=request.user,
            match=match,
            competition=competition,
            defaults={'predicted_winner': winner}
        )

    messages.success(request, 'Knockout predictions saved.')
    return redirect('predictions:knockout')


@login_required
def my_predictions_view(request):
    from payments.models import Payment

    payment = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).first()

    if not payment:
        predictions = Prediction.objects.none()
    else:
        predictions = Prediction.objects.filter(
            user=request.user,
            competition=payment.tier.competition
        ).select_related(
            'match', 'match__home_team', 'match__away_team', 'competition'
        ).order_by('-match__kickoff_time')

    return render(request, 'predictions/my_predictions.html', {
        'predictions': predictions
    })