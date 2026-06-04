from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('tiers/', views.tier_selection_view, name='tiers'),
    path('checkout/<int:tier_id>/', views.checkout_view, name='checkout'),
    path('initiate/<int:tier_id>/', views.initiate_payment, name='initiate'),
    path('verify/', views.verify_payment, name='verify'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('referrals/', views.referrals_view, name='referrals'),
]
