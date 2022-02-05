from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),

    # Below API calls use POST method
    path('api/get_access_token/', views.ExchangeToken.as_view(), name='get-access-token'),
    path('api/get_transactions/', views.GetTransaction.as_view(), name='get-transaction'),

    # Below API calls use GET method
    path('api/identity/', views.Identity.as_view(), name='get-identity'),
    path('api/balance/', views.Balance.as_view(), name='get-balance'),
    path('api/item/', views.ItemInfo.as_view(), name='get-item-info'),
    path('api/accounts/', views.AccountInfo.as_view(), name='get-account-info'),
    path('api/webhook/', views.webhook, name='webhook'),
]