from . import views
from django.urls import path

urlpatterns = [
    path('api/getadminuser/', views.GetAdminUser.as_view(), name='get_admin_user')
]