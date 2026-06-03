from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match
from services.scoring import process_match_predictions


@receiver(post_save, sender=Match)
def trigger_scoring_on_result(sender, instance, **kwargs):
    """
    Fires every time a Match is saved.
    Only processes scoring when:
    - match is marked completed
    - both scores are entered
    - predictions haven't been scored yet
    """
    match = instance

    if match.status != Match.Status.COMPLETED:
        return

    if match.home_score is None or match.away_score is None:
        return

    # Only process if there are unscored predictions
    from predictions.models import Prediction
    unscored = Prediction.objects.filter(
        match=match,
        is_scored=False
    ).exists()

    if not unscored:
        return

    process_match_predictions(match)