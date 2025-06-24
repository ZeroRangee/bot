from django.db import models
from django.utils import timezone
import uuid

class Message(models.Model):
    MESSAGE_SOURCES = [
        ('web', 'Web Interface'),
        ('telegram', 'Telegram Bot'),
    ]
    
    MESSAGE_DIRECTIONS = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    source = models.CharField(max_length=10, choices=MESSAGE_SOURCES)
    direction = models.CharField(max_length=10, choices=MESSAGE_DIRECTIONS)
    telegram_user_id = models.CharField(max_length=100, blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    telegram_message_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source} - {self.direction}: {self.text[:50]}"

class TelegramUser(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.username or self.first_name} ({self.telegram_id})"