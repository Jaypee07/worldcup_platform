from predictions.models import Prediction
from tournaments.models import Match

def score_group_prediction(prediction: Prediction) -> int:
    match = prediction.match

    if match.home_score is None or match.away_score is None:
        return 0

    actual = match.get_result()
    predicted = prediction.get_predicted_outcome()

    if predicted is None:
        return 0

    # Exact score — 5 points
    if (prediction.predicted_home_score == match.home_score and
            prediction.predicted_away_score == match.away_score):
        return 5

    # Correct outcome only — 3 points
    if predicted == actual:
        return 3

    return 0


def score_knockout_prediction(prediction: Prediction) -> int:
    match = prediction.match

    if match.home_score is None or match.away_score is None:
        return 0

    if match.home_score > match.away_score:
        actual_winner = match.home_team
    elif match.away_score > match.home_score:
        actual_winner = match.away_team
    else:
        actual_winner = None

    if actual_winner is None or prediction.predicted_winner is None:
        return 0

    return 2 if prediction.predicted_winner == actual_winner else 0


def process_match_predictions(match: Match):
    predictions = Prediction.objects.filter(match=match, is_scored=False)

    for prediction in predictions:
        if match.stage == Match.Stage.GROUP:
            points = score_group_prediction(prediction)
        else:
            points = score_knockout_prediction(prediction)

        prediction.points_awarded = points
        prediction.is_scored = True
        prediction.save()

    update_leaderboard(match)


def update_leaderboard(match: Match):
    from leaderboard.models import LeaderboardEntry
    from django.db.models import Sum

    predictions = Prediction.objects.filter(match=match)
    affected = predictions.values_list('user', 'competition').distinct()

    for user_id, competition_id in affected:
        total = Prediction.objects.filter(
            user_id=user_id,
            competition_id=competition_id,
            is_scored=True
        ).aggregate(total=Sum('points_awarded'))['total'] or 0

        entry, _ = LeaderboardEntry.objects.get_or_create(
            user_id=user_id,
            competition_id=competition_id
        )
        entry.total_points = total
        entry.save()

    recompute_ranks(match)


def recompute_ranks(match: Match):
    from leaderboard.models import LeaderboardEntry
    from predictions.models import Competition

    competitions = Competition.objects.filter(
        prediction__match=match
    ).distinct()

    for competition in competitions:
        entries = LeaderboardEntry.objects.filter(
            competition=competition
        ).order_by('-total_points')

        for rank, entry in enumerate(entries, start=1):
            entry.rank = rank
            entry.save()