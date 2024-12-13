from django.urls import path
from .views import signInElder, signInFamily, MonthCalendar, add_schedule
from . import views

app_name = 'careLink'
urlpatterns = [
    path('login', views.login, name="login"),
    path('signin_elder', signInElder.as_view(), name='signin_elder'),
    path('signin_family', signInFamily.as_view(), name='signin_family'),
    path('family/schedule/', MonthCalendar.as_view(), name='calendar'),
    path('family/<int:year>/<int:month>/', MonthCalendar.as_view(), name='calendar'),
    path('family/schedule/<str:date>/', add_schedule, name='add_schedule'),
]