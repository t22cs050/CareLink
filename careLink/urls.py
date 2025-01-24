from django.urls import path
from .views import signUpElder, signUpFamily, MonthCalendar, add_schedule
from . import views
from .views import get_schedules


app_name = 'careLink'
urlpatterns = [
    path('login', views.user_login, name="user_login"),
    path('signup_elder', signUpElder.as_view(), name='signup_elder'),
    path('signup_family', signUpFamily.register, name='signup_family'),
    path('elder/home', views.elderHome, name='elder_home'),

    path('family/schedule/', MonthCalendar.as_view(), name='calendar'),
    path('family/<int:year>/<int:month>/', MonthCalendar.as_view(), name='calendar'),
    path('family/schedule/<str:date>/', add_schedule, name='add_schedule'),
    path('family/image/', views.result_view, name='image_save'),
    path('family/result/', views.result_view, name='result'),
    path('family/help/',views.family_help, name='family_help'),
    
    path('save_order/', views.save_order, name='save_order'),
    path('delete_schedule/', views.delete_schedule, name='delete_schedule'),
    path('delete-image/', views.delete_image, name='delete_image'),

    path('get_schedules/', get_schedules, name='get_schedules'),
    path('update_schedule/', views.update_schedule, name='update_schedule'),
    path('elder/effect',views.AllCompleteEffect.as_view(),name='all_complete_effect'),
    path('elder/logout/', views.elder_logout, name='elder_logout'),
    path('change_elder_name/', views.change_elder_name, name='change_name'),
    path('emergency_login/',views.emergency_login, name='emergency_login'),

]
    
