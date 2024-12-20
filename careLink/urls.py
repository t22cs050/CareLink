from django.urls import path
from .views import signUpElder, signUpFamily, MonthCalendar, add_schedule
from . import views
from .views import get_schedules

app_name = 'careLink'
urlpatterns = [
    path('login', views.user_login, name="login"),
    path('signup_elder', signUpElder.as_view(), name='signup_elder'),
    path('signup_family', signUpFamily.register, name='signup_family'),
    path('family/schedule/', MonthCalendar.as_view(), name='calendar'),
    path('family/<int:year>/<int:month>/', MonthCalendar.as_view(), name='calendar'),
    path('family/schedule/<str:date>/', add_schedule, name='add_schedule'),
    path('family/result/', views.result_view, name='result'),
    path('get_schedules/', get_schedules, name='get_schedules'),
]