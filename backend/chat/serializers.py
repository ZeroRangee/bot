from rest_framework import serializers
from .models import Message, TelegramUser

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'source', 'direction', 'telegram_user_id', 
                 'telegram_username', 'telegram_message_id', 'created_at']

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'username', 'first_name', 'last_name', 
                 'is_active', 'created_at']