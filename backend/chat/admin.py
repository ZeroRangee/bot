from django.contrib import admin
from .models import Message, TelegramUser

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text', 'source', 'direction', 'telegram_username', 'created_at']
    list_filter = ['source', 'direction', 'created_at']
    search_fields = ['text', 'telegram_username']
    readonly_fields = ['id', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['created_at']