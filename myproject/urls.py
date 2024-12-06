from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('careLink/', include('careLink.urls'), name='careLink'),
]
