from django.urls import path
from . import views

urlpatterns = [
    # Public interfaces
    path('', views.index, name='index'),
    path('admin-chat/', views.admin_chat, name='admin_chat'),
    
    # API endpoints
    path('messages/', views.get_messages, name='get_messages'),
    path('users/', views.get_telegram_users, name='get_telegram_users'),
    path('send/', views.send_message, name='send_message'),
    
    # Admin API endpoints
    path('admin/sessions/', views.get_chat_sessions, name='get_chat_sessions'),
    path('admin/send/', views.send_admin_message, name='send_admin_message'),
    path('admin/broadcast/', views.broadcast_message, name='broadcast_message'),
    path('admin/stats/', views.get_documents_stats, name='get_documents_stats'),
    path('admin/user/<str:telegram_user_id>/documents/', views.get_user_documents, name='get_user_documents'),
    
    # AI and webhook endpoints
    path('ai-chat/', views.ai_chat_api, name='ai_chat_api'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
]