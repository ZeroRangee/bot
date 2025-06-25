from django.contrib import admin
from .models import Message, TelegramUser, ChatSession, Document, ApplicantProfile, BroadcastMessage, ScrapedContent

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['telegram_id', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'source', 'direction', 'message_type', 'telegram_user_info', 'created_at']
    list_filter = ['source', 'direction', 'message_type', 'created_at']
    search_fields = ['text', 'telegram_user__username', 'telegram_user__first_name']
    readonly_fields = ['id', 'created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'
    
    def telegram_user_info(self, obj):
        if obj.telegram_user:
            return f"{obj.telegram_user.username or obj.telegram_user.first_name} ({obj.telegram_user.telegram_id})"
        return "N/A"
    telegram_user_info.short_description = 'Telegram User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('telegram_user').order_by('-created_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'telegram_user_info', 'session_type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['session_type', 'is_active', 'created_at']
    search_fields = ['telegram_user__username', 'telegram_user__first_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def telegram_user_info(self, obj):
        return f"{obj.telegram_user.username or obj.telegram_user.first_name} ({obj.telegram_user.telegram_id})"
    telegram_user_info.short_description = 'Telegram User'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'document_type', 'telegram_user_info', 'file_size_mb', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['file_name', 'telegram_user__username', 'telegram_user__first_name']
    readonly_fields = ['id', 'file_id', 'created_at']
    
    def telegram_user_info(self, obj):
        return f"{obj.telegram_user.username or obj.telegram_user.first_name} ({obj.telegram_user.telegram_id})"
    telegram_user_info.short_description = 'Telegram User'
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "Unknown"
    file_size_mb.short_description = 'File Size'

@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ['telegram_user_info', 'school_name', 'graduation_year', 'city', 'desired_faculty', 'created_at']
    list_filter = ['graduation_year', 'city', 'created_at']
    search_fields = ['school_name', 'city', 'telegram_user__username', 'telegram_user__first_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def telegram_user_info(self, obj):
        return f"{obj.telegram_user.username or obj.telegram_user.first_name} ({obj.telegram_user.telegram_id})"
    telegram_user_info.short_description = 'Telegram User'

@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ['message_preview', 'sender', 'target_user_type', 'sent_count', 'created_at']
    list_filter = ['target_user_type', 'created_at']
    search_fields = ['message_text', 'sender__username']
    readonly_fields = ['id', 'sent_count', 'created_at']
    filter_horizontal = ['target_users']
    
    def message_preview(self, obj):
        return obj.message_text[:50] + '...' if len(obj.message_text) > 50 else obj.message_text
    message_preview.short_description = 'Message'

@admin.register(ScrapedContent)
class ScrapedContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'is_active', 'scraped_at']
    list_filter = ['is_active', 'scraped_at']
    search_fields = ['title', 'url', 'content']
    readonly_fields = ['scraped_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-scraped_at')

# Custom admin site title
admin.site.site_header = "МВЭУ - Администрирование бота"
admin.site.site_title = "МВЭУ Admin"
admin.site.index_title = "Панель администрирования"