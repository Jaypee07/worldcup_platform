from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.year}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)  # e.g. "BRA", "ENG"
    flag = models.CharField(max_length=10, blank=True)  # emoji or image path

    def __str__(self):
        return self.name


class Group(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)  # e.g. "A", "B"
    teams = models.ManyToManyField(Team)

    def __str__(self):
        return f"Group {self.name}"


class Match(models.Model):
    class Stage(models.TextChoices):
        GROUP = 'group', 'Group Stage'
        R16 = 'r16', 'Round of 16'
        QF = 'qf', 'Quarter Final'
        SF = 'sf', 'Semi Final'
        FINAL = 'final', 'Final'

    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming'
        LIVE = 'live', 'Live'
        COMPLETED = 'completed', 'Completed'

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    stage = models.CharField(max_length=10, choices=Stage.choices, default=Stage.GROUP)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    kickoff_time = models.DateTimeField()

    # Actual results (admin fills these in)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.stage})"

    def get_result(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return 'home'
        elif self.away_score > self.home_score:
            return 'away'
        return 'draw'