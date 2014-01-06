from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from demoscene.shortcuts import *
from demoscene.forms.account import *
from demoscene.models import AccountProfile, CaptchaQuestion
from read_only_mode import writeable_site_required


@writeable_site_required
@login_required
def index(request):
	return render(request, 'accounts/index.html', {})


@writeable_site_required
def signup(request):
	if request.method == 'POST':
		captcha = CaptchaQuestion.objects.get(id=request.session.get('captcha_id'))

		form = UserSignupForm(request.POST, captcha=captcha)
		if form.is_valid():
			form.save()
			user = authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1'],
			)
			login(request, user)
			messages.success(request, 'Account created')
			return redirect('home')
	else:
		captcha = CaptchaQuestion.objects.order_by('?')[0]
		request.session['captcha_id'] = captcha.id
		form = UserSignupForm(captcha=captcha)
	return render(request, 'accounts/signup.html', {
		'form': form,
	})


@writeable_site_required
@login_required
def preferences(request):
	try:
		profile = request.user.get_profile()
	except AccountProfile.DoesNotExist:
		profile = AccountProfile(user=request.user)
	if request.method == 'POST':
		form = AccountPreferencesForm(request.POST, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, 'Preferences updated')
			return redirect('home')
	else:
		form = AccountPreferencesForm(instance=profile)

	return render(request, 'shared/simple_form.html', {
		'form': form,
		'title': "Preferences",
		'html_title': "Preferences",
		'action_url': reverse('account_preferences'),
	})


@writeable_site_required
@login_required
def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Password updated')
			return redirect('home')
	else:
		form = PasswordChangeForm(request.user)

	return render(request, 'shared/simple_form.html', {
		'form': form,
		'title': "Change password",
		'html_title': "Change password",
		'action_url': reverse('account_change_password'),
	})
