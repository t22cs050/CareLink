from django.urls import path
from .views import signUpElder, signUpFamily, MonthCalendar, MonthCalendar
from . import views


app_name = 'careLink'
urlpatterns = [
    path('login', views.login, name="login"),
    path('signup_elder', signUpElder.as_view(), name='signup_elder'),
    path('signup_family', signUpFamily.as_view(), name='signup_family'),
    path('family/result-calender', MonthCalendar.as_view(), name='result-calender'),
    path('family/result-calender/result', views.result, name="result"),
    path('family/<int:year>/<int:month>/', MonthCalendar.as_view(), name='month'),
]