from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import requests
import uuid

from .models import (
    TournamentTier, Payment, Wallet,
    ReferralCode, Referral, EmailVerification
)
from accounts.models import Profile


def generate_reference():
    return f"WC2026-{uuid.uuid4().hex[:12].upper()}"


@login_required
def tier_selection_view(request):
    tiers = TournamentTier.objects.select_related('competition').all()
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    paid_payment = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).first()

    paid_tier_ids = [paid_payment.tier_id] if paid_payment else []
    has_paid = paid_payment is not None

    return render(request, 'payments/tiers.html', {
        'tiers': tiers,
        'wallet': wallet,
        'paid_tier_ids': paid_tier_ids,
        'has_paid': has_paid,
    })


@login_required
def checkout_view(request, tier_id):
    tier = get_object_or_404(TournamentTier, id=tier_id)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    any_paid = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).exists()

    if any_paid:
        messages.info(request, 'You have already joined a tier.')
        return redirect('payments:tiers')

    balance_to_use = min(wallet.balance, tier.entry_fee)
    amount_to_pay = tier.entry_fee - balance_to_use

    return render(request, 'payments/checkout.html', {
        'tier': tier,
        'wallet': wallet,
        'balance_to_use': balance_to_use,
        'amount_to_pay': amount_to_pay,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    })


@login_required
def initiate_payment(request, tier_id):
    if request.method != 'POST':
        return redirect('payments:tiers')

    tier = get_object_or_404(TournamentTier, id=tier_id)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    any_paid = Payment.objects.filter(
        user=request.user,
        status=Payment.Status.SUCCESS
    ).exists()

    if any_paid:
        messages.info(request, 'You have already joined a tier.')
        return redirect('payments:tiers')

    balance_to_use = min(wallet.balance, tier.entry_fee)
    amount_to_pay = tier.entry_fee - balance_to_use

    reference = generate_reference()

    payment = Payment.objects.create(
        user=request.user,
        tier=tier,
        reference=reference,
        amount=tier.entry_fee,
        status=Payment.Status.PENDING,
        used_balance=balance_to_use,
    )

    if amount_to_pay == 0:
        wallet.debit(balance_to_use)
        payment.status = Payment.Status.SUCCESS
        payment.save()
        process_successful_payment(request.user, tier, reference)
        messages.success(
            request,
            f'Joined {tier.name} using wallet balance!'
        )
        return redirect('payments:tiers')

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        'email': request.user.email,
        'amount': amount_to_pay * 100,
        'reference': reference,
        'callback_url': request.build_absolute_uri('/payments/verify/'),
        'metadata': {
            'user_id': request.user.id,
            'tier_id': tier.id,
            'balance_used': balance_to_use,
        }
    }

    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers,
        json=payload
    )

    data = response.json()

    if data.get('status'):
        return redirect(data['data']['authorization_url'])
    else:
        payment.status = Payment.Status.FAILED
        payment.save()
        messages.error(request, 'Payment initiation failed. Try again.')
        return redirect('payments:checkout', tier_id=tier_id)


@login_required
def verify_payment(request):
    reference = request.GET.get('reference')

    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('payments:tiers')

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{reference}',
        headers=headers
    )

    data = response.json()

    if not data.get('status'):
        messages.error(request, 'Payment verification failed.')
        return redirect('payments:tiers')

    paystack_data = data['data']

    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
        return redirect('payments:tiers')

    if paystack_data['status'] == 'success':
        if payment.status != Payment.Status.SUCCESS:
            payment.status = Payment.Status.SUCCESS
            payment.save()

            if payment.used_balance > 0:
                wallet, _ = Wallet.objects.get_or_create(
                    user=request.user
                )
                wallet.debit(payment.used_balance)

            process_successful_payment(
                request.user, payment.tier, reference
            )

        messages.success(
            request,
            f'Payment successful! You have joined {payment.tier.name}.'
        )
    else:
        payment.status = Payment.Status.FAILED
        payment.save()
        messages.error(request, 'Payment was not successful.')

    return redirect('payments:tiers')


def process_successful_payment(user, tier, reference):
    try:
        profile = user.profile
        referral_code = profile.referred_by_code

        if referral_code:
            try:
                ref_code_obj = ReferralCode.objects.get(code=referral_code)
                referrer = ref_code_obj.user

                if referrer != user:
                    reward = int(tier.entry_fee * 0.20)

                    referral, created = Referral.objects.get_or_create(
                        referrer=referrer,
                        referee=user,
                        tier=tier,
                        defaults={
                            'reward_amount': reward,
                            'is_paid': False
                        }
                    )

                    if created:
                        wallet, _ = Wallet.objects.get_or_create(
                            user=referrer
                        )
                        wallet.credit(reward)
                        referral.is_paid = True
                        referral.save()

            except ReferralCode.DoesNotExist:
                pass
    except Exception:
        pass


@login_required
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    referrals = Referral.objects.filter(
        referrer=request.user
    ).select_related('referee', 'tier').order_by('-created_at')

    try:
        ref_code = ReferralCode.objects.get(user=request.user)
    except ReferralCode.DoesNotExist:
        import secrets
        import string
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        ref_code = ReferralCode.objects.create(user=request.user, code=code)

    referral_link = request.build_absolute_uri(
        f'/accounts/register/?ref={ref_code.code}'
    )

    return render(request, 'payments/wallet.html', {
        'wallet': wallet,
        'referrals': referrals,
        'ref_code': ref_code,
        'referral_link': referral_link,
    })


@login_required
def referrals_view(request):
    referrals = Referral.objects.filter(
        referrer=request.user
    ).select_related('referee', 'tier').order_by('-created_at')

    total_earned = sum(r.reward_amount for r in referrals if r.is_paid)

    return render(request, 'payments/referrals.html', {
        'referrals': referrals,
        'total_earned': total_earned,
    })


