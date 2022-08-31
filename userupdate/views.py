from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from .models import PendingPilot
from django.views import View
from .creds import settings
from django.contrib.auth.models import User

from .forms import NameForm
from fusionauth.fusionauth_client import FusionAuthClient

# Create your views here.

def home(request):
    return render(request, 'home.html', {})

def get_or_create_user(user_id, request):
  user = User.objects.filter(username=user_id).first()

  if not user:
    print('No User')

  return user


def get_login_url(request):
  redirect_url = request.build_absolute_uri(reverse("dashboard"))
  login_url = f"{settings.FUSION_AUTH_BASE_URL}/oauth2/authorize?client_id={settings.FUSION_AUTH_APP_ID}&redirect_uri={redirect_url}&response_type=code"

  login_url = login_url.format(
    settings.FUSION_AUTH_BASE_URL, settings.FUSION_AUTH_APP_ID,
  )
  return login_url


def user_login_ok(request):
  client = FusionAuthClient(
    settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL
  )

  code = request.GET.get("code")

  if not code:
    print("no code")
    return False

  try:
    redirect_url = request.build_absolute_uri(reverse("dashboard"))
    # if you are using version 1.19.x of the python library or later, use this
    r = client.exchange_o_auth_code_for_access_token(
      code,
      settings.FUSION_AUTH_APP_ID,
      redirect_url,
      settings.FUSION_AUTH_CLIENT_SECRET,
    )

    if r.was_successful():
      access_token = r.success_response["access_token"]
      user_id = r.success_response["userId"]
      get_or_create_user(user_id, request)
      return user_id
    else:
      print(r.error_response)
      return False

  except Exception as e:
    print(e)


class DashboardView(View):

  def get(self, request):

    user_id = user_login_ok(request)
    print('user id', user_id)
    if not user_id:
        login_url = get_login_url(request)
        return redirect(login_url)

    birthday = None
    user = None

    try:
      client = FusionAuthClient(settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL)
      r = client.retrieve_user(user_id)
      print(r)
      if r.was_successful():
          user = r.success_response
          birthday = user["user"]["birthDate"]
          firstname = user["user"]["firstName"]
          lastname = user["user"]["lastName"]
      else:
          print(r.error_response)
    except Exception as e:
        print("couldn't get user")
        print(e)

    return render(request, "dashboard.html", {"birthday": birthday, "firstname": firstname, "lastname": lastname})


class LogoutView(View):

  def get(self, request, *args, **kwargs):
    redirect_url = request.build_absolute_uri("home")
    url = f"{settings.FUSION_AUTH_BASE_URL}/oauth2/logout?client_id={settings.FUSION_AUTH_APP_ID}"
    return redirect(url)


class yourinfo(View):
    def get(self, request):
        form = NameForm

        num_users = User.objects.count()
        login_url = get_login_url(request)

        return render(request, 'home.html', {'form': form, "login_url": login_url, "num_users": num_users})

    def post(self, request):
        form = NameForm(request.POST)
        if form.is_valid():
            obj, create = PendingPilot.objects.get_or_create(e_id=form.cleaned_data['e_id'],
                                                             first_name = form.cleaned_data['first_name'],
                                                             last_name = form.cleaned_data['last_name'],
                                                             extra = form.cleaned_data['extra'],
                                                             approved = False)
            return HttpResponseRedirect('/')
        return render(request, 'home.html', {'form': form})
