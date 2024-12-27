from django.urls import path
from .views import signUpElder, signUpFamily, MonthCalendar, add_schedule
from . import views


app_name = 'careLink'
urlpatterns = [
    path('login', views.user_login, name="login"),
    path('signup_elder', signUpElder.as_view(), name='signup_elder'),
    path('signup_family', signUpFamily.register, name='signup_family'),
    path('elder/home', views.elderHome, name='elder_home'),
    path('family/schedule/', MonthCalendar.as_view(), name='calendar'),
    path('family/<int:year>/<int:month>/', MonthCalendar.as_view(), name='calendar'),
    path('family/schedule/<str:date>/', add_schedule, name='add_schedule'),
    path('update_schedule', views.update_schedule, name="update_schedule")
]