from django.db import models
from django.contrib.auth.models import User
from predictions.models import Competition


class TournamentTier(models.Model):
    competition = models.OneToOneField(
        Competition, on_delete=models.CASCADE
    )
    entry_fee = models.IntegerField()  # in Naira
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} — ₦{self.entry_fee}"

    def prize_pool(self):
        paid = Payment.objects.filter(
            tier=self, status=Payment.Status.SUCCESS
        ).count()
        return int(self.entry_fee * paid * 0.8)

    def first_prize(self):
        return int(self.prize_pool() * 0.5)

    def second_prize(self):
        return int(self.prize_pool() * 0.3)

    def third_prize(self):
        return int(self.prize_pool() * 0.2)


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(TournamentTier, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()  # in Naira
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    used_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tier')

    def __str__(self):
        return f"{self.user.username} — {self.tier.name} — {self.status}"


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)  # in Naira

    def __str__(self):
        return f"{self.user.username} — ₦{self.balance}"

    def credit(self, amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.code}"


class Referral(models.Model):
    referrer = models.ForeignKey(
        User, related_name='referrals_made',
        on_delete=models.CASCADE
    )
    referee = models.ForeignKey(
        User, related_name='referred_by',
        on_delete=models.CASCADE
    )
    tier = models.ForeignKey(TournamentTier, on_delete=models.CASCADE)
    reward_amount = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('referrer', 'referee', 'tier')

    def __str__(self):
        return f"{self.referrer.username} → {self.referee.username}"


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — verified: {self.is_verified}"