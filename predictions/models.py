from django.db import models
from django.contrib.auth.models import User
from tournaments.models import Match, Team


class Competition(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    predicted_home_score = models.IntegerField(null=True, blank=True)
    predicted_away_score = models.IntegerField(null=True, blank=True)
    predicted_winner = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL
    )

    points_awarded = models.IntegerField(default=0)
    is_scored = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'match', 'competition')

    def __str__(self):
        return f"{self.user.username} — {self.match}"

    def get_predicted_outcome(self):
        if self.predicted_home_score is None or self.predicted_away_score is None:
            return None
        if self.predicted_home_score > self.predicted_away_score:
            return 'home'
        elif self.predicted_away_score > self.predicted_home_score:
            return 'away'
        return 'draw'