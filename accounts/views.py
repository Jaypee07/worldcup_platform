from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm = request.POST['password2']
        ref_code = request.POST.get('ref_code', '').strip().upper()

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html',
                         {'ref_code': ref_code})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html',
                         {'ref_code': ref_code})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html',
                         {'ref_code': ref_code})

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        Profile.objects.create(
            user=user,
            referred_by_code=ref_code
        )

        # Create email verification token
        import secrets
        from payments.models import EmailVerification
        token = secrets.token_hex(32)
        EmailVerification.objects.create(user=user, token=token)

        # Send verification email
        send_verification_email(request, user, token)

        messages.success(
            request,
            'Account created. Please check your email to verify.'
        )
        return redirect('accounts:login')

    ref_code = request.GET.get('ref', '')
    return render(request, 'accounts/register.html', {'ref_code': ref_code})


def send_verification_email(request, user, token):
    from django.core.mail import send_mail
    verify_url = request.build_absolute_uri(
        f'/accounts/verify-email/{token}/'
    )
    send_mail(
        subject='Verify your WC2026 Predictor account',
        message=f'Hi {user.username},\n\nClick the link below to verify your email:\n\n{verify_url}\n\nThis link is valid for 24 hours.',
        from_email='noreply@wc2026predictor.com',
        recipient_list=[user.email],
        fail_silently=False,
    )


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('tournaments:home')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

def verify_email_view(request, token):
    from payments.models import EmailVerification
    try:
        verification = EmailVerification.objects.get(
            token=token, is_verified=False
        )
        verification.is_verified = True
        verification.save()
        messages.success(
            request,
            'Email verified successfully. You can now join a tournament.'
        )
    except EmailVerification.DoesNotExist:
        messages.error(
            request,
            'Invalid or already used verification link.'
        )
    return redirect('accounts:login')