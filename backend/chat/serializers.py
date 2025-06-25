from rest_framework import serializers
from .models import Message, TelegramUser, Document, ChatSession, ApplicantProfile, BroadcastMessage

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'username', 'first_name', 'last_name', 
                 'user_type', 'is_active', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    telegram_user = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'text', 'source', 'direction', 'message_type',
                 'telegram_user', 'telegram_message_id', 'created_at']

class DocumentSerializer(serializers.ModelSerializer):
    telegram_user = TelegramUserSerializer(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'telegram_user', 'document_type', 'document_type_display',
                 'file_id', 'file_name', 'file_size', 'description', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    telegram_user = TelegramUserSerializer(read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'telegram_user', 'session_type', 'session_type_display',
                 'is_active', 'created_at', 'updated_at', 'message_count', 'last_message_time']
    
    def get_message_count(self, obj):
        return Message.objects.filter(telegram_user=obj.telegram_user).count()
    
    def get_last_message_time(self, obj):
        last_message = Message.objects.filter(telegram_user=obj.telegram_user).first()
        return last_message.created_at if last_message else None

class ApplicantProfileSerializer(serializers.ModelSerializer):
    telegram_user = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = ApplicantProfile
        fields = ['telegram_user', 'school_name', 'graduation_year', 'city',
                 'phone', 'email', 'desired_faculty', 'created_at', 'updated_at']

class BroadcastMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    target_user_type_display = serializers.CharField(source='get_target_user_type_display', read_only=True)
    
    class Meta:
        model = BroadcastMessage
        fields = ['id', 'sender_username', 'message_text', 'target_user_type',
                 'target_user_type_display', 'sent_count', 'created_at']