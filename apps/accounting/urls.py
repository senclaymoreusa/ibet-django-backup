from django.urls import path, include
from . import views

urlpatterns = [
    path('api/deposit_method', views.getDepositMethod.as_view(), name = 'deposit_method'),
    path('api/get_BankList', views.getBankList.as_view(), name = 'get_BankList'),
]