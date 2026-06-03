from django.contrib import admin
from .models import (
    TournamentTier, Payment, Wallet,
    ReferralCode, Referral, EmailVerification
)


@admin.register(TournamentTier)
class TournamentTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'entry_fee', 'competition']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'tier', 'amount',
        'status', 'reference', 'created_at'
    ]
    list_filter = ['status', 'tier']
    search_fields = ['user__username', 'reference']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']
    search_fields = ['user__username']


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at']
    search_fields = ['user__username', 'code']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = [
        'referrer', 'referee', 'tier',
        'reward_amount', 'is_paid', 'created_at'
    ]
    list_filter = ['is_paid', 'tier']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'created_at']
    list_filter = ['is_verified']