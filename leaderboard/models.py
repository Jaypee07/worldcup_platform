from django.conf import settings
from django.db import models
from predictions.models import Competition


class LeaderboardEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-total_points']
        unique_together = ('user', 'competition')

    def __str__(self):
        return f"{self.user} — {self.competition} ({self.total_points})"
