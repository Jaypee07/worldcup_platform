from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    referred_by_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def is_email_verified(self):
        try:
            return self.user.emailverification.is_verified
        except:
            return False

    def has_paid_for_tier(self, tier):
        from payments.models import Payment
        return Payment.objects.filter(
            user=self.user,
            tier=tier,
            status=Payment.Status.SUCCESS
        ).exists()