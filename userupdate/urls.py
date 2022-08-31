from django.urls import path
from . import views

urlpatterns = [
    path('', views.yourinfo.as_view(), name="home"),
    path('yourinfo', views.yourinfo.as_view(), name="Your info"),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('logout', views.LogoutView.as_view(), name='logout'),
]