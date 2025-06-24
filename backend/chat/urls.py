from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('messages/', views.get_messages, name='get_messages'),
    path('users/', views.get_telegram_users, name='get_telegram_users'),
    path('send/', views.send_message, name='send_message'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
]