from django.urls import path
from .views import signInElder,signInFamily,result_view
from . import views


app_name = 'careLink'
urlpatterns = [
    path('login', views.login, name="login"),
    path('signin_elder', signInElder.as_view(), name='signin_elder'),
    path('signin_family', signInFamily.as_view(), name='signin_family'),
    

    #管理者側の行動状況の確認画面
    path('family/result',result_view,name='result')

]