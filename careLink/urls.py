from django.urls import path
from .views import signInElder, signInFamily
from . import views

app_name = 'careLink'
urlpatterns = [
    path('login', views.login, name="login"),
    path('signin_elder', signInElder.as_view(), name='signin_elder'),
    path('signin_family', signInFamily.as_view(), name='signin_family'),
]