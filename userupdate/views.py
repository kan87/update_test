from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Pilot
from django.views import View
from .creds import settings
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.contrib import messages

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


def dashboard(request):
  template_name = 'dashboard.html'
  form_class = NameForm

  if request.method == 'GET':
    user_id = user_login_ok(request)
    if not user_id:
      login_url = get_login_url(request)
      return redirect(login_url)

    birthday = None
    user = None

    try:
      client = FusionAuthClient(settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL)
      r = client.retrieve_user(user_id)
      if r.was_successful():
        print('success')
        user = r.success_response
        email = user["user"]["email"]  # Get email as unique identifier of user
        firstname = user["user"]["firstName"]  # Change data to use email in prod
        prefill = Pilot.objects.get(first_name=firstname)  # Change data to use email in prod
        birthday = user["user"]["birthDate"]

        form = form_class(instance=prefill)

        return render(request, template_name,
                      {'form': form, 'birthday': birthday, 'first_name': prefill.first_name,
                       'last_name': prefill.last_name, 'email': email})

      else:
        print(r.error_response)
    except Exception as e:
      form = form_class
      print('Error:', e)
      return render(request, template_name, {'form': form, 'birthday': birthday, 'email': email})

  elif request.method == 'POST':
    form = form_class(request.POST)
    # try:
    if form.is_valid():
      obj, create = Pilot.objects.update_or_create(e_id=form.cleaned_data['e_id'],
                                                   defaults={'first_name': form.cleaned_data['first_name'],
                                                             'last_name': form.cleaned_data['last_name'],
                                                             'extra': form.cleaned_data['extra'],
                                                             'extra_locked': form.cleaned_data['extra locked']},
                                                   approved=False)
      print('good to go')
      return HttpResponseRedirect('dashboard')
    else:
      print('error 2')
      return render(request, 'dashboard.html', {'form': form})


class DashboardView(FormView):
  template_name = 'dashboard.html'
  form_class = NameForm
  def get(self, request):
  # Get logged in user info
      user_id = user_login_ok(request)
      if not user_id:
          login_url = get_login_url(request)
          return redirect(login_url)

      birthday = None
      user = None

      try:
        client = FusionAuthClient(settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL)
        r = client.retrieve_user(user_id)
        if r.was_successful():
            print('success')
            user = r.success_response
            email = user["user"]["email"]  # Get email as unique identifier of user
            firstname = user["user"]["firstName"] # Change data to use email in prod
            prefill = Pilot.objects.get(first_name=firstname) # Change data to use email in prod
            birthday = user["user"]["birthDate"]

            form = self.form_class(instance=prefill)

            # form.fields['e_id'].disabled = True

            request.session['check_e_id'] = prefill.e_id  # Stores check_e_id to prevent tampering
            request.session['email'] = email
            request.session['first_name'] = prefill.first_name
            request.session['last_name'] = prefill.last_name
            request.session['birthday'] = birthday


            print('In GET', request.session['check_e_id'])


            return render(request, self.template_name, {'form': form, 'birthday': birthday, 'first_name': prefill.first_name,
                                                     'last_name': prefill.last_name, 'email': email})

        else:
            print(r.error_response)
      except Exception as e:
          form = self.form_class
          print('Error:', e)
          return render(request, self.template_name, {'form': form, 'birthday': birthday, 'email': email})

  def post(self, request):
    form = self.form_class(request.POST)
    instance = Pilot.objects.get(e_id=form['e_id'].value())
    print(instance)
    form = self.form_class(request.POST, instance=instance)
    print('post 1')

    context = {'form': form, 'birthday': request.session['birthday'], 'first_name': request.session['first_name'],
               'last_name': request.session['last_name'], 'email': request.session['email']}

    if form.is_valid():
      pilot_data = Pilot.objects.get(e_id=form['e_id'].value())
      print('pilot eid', pilot_data.e_id)
      print('in POST', request.session['check_e_id'])
      if pilot_data.e_id == request.session['check_e_id']:
        pilot_data.first_name = form['first_name'].value()
        pilot_data.last_name = form['last_name'].value()
        pilot_data.extra = form['extra'].value()
        pilot_data.extra_locked = form['extra_locked'].value()
        pilot_data.approved = False
        pilot_data.save()
        print('good to go')

        return render(request, 'dashboard.html', context)
      else:
        print('bad eid')
        messages.warning(request, 'Incorrect Employee ID')
        return render(request, 'dashboard.html', context)
    else:
      print('error 2')
      return render(request, 'dashboard.html', context)
  
    # def form_valid(self, form):
    #   print('form valid here')
    #   obj, create = Pilot.objects.update_or_create(e_id=form.cleaned_data['e_id'],
    #                                                defaults={'first_name': form.cleaned_data['first_name'],
    #                                                        'last_name': form.cleaned_data['last_name'],
    #                                                        'extra': form.cleaned_data['extra'],
    #                                                        'extra_locked': form.cleaned_data['extra_locked']},
    #                                              approved=False)
    # 
    #   print('good to go')
    #   return super().form_valid(form)
    # return render(request, 'dashboard.html', {'form': form})


class LogoutView(View):

  def get(self, request, *args, **kwargs):
    redirect_url = request.build_absolute_uri("home")
    url = f"{settings.FUSION_AUTH_BASE_URL}/oauth2/logout?client_id={settings.FUSION_AUTH_APP_ID}"
    return redirect(url)
