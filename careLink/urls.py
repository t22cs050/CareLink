from django.urls import path
from .views import signUpElder, signUpFamily
from . import views

app_name = 'careLink'
urlpatterns = [
    path('login', views.login, name="login"),
    path('signup_elder', signUpElder.as_view(), name='signup_elder'),
    path('signup_family', signUpFamily.as_view(), name='signup_family'),
]