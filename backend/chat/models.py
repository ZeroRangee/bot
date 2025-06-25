from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class TelegramUser(models.Model):
    USER_TYPES = [
        ('applicant', 'Абитуриент'),
        ('student', 'Студент'),
        ('admin', 'Администратор'),
    ]
    
    telegram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.username or self.first_name} ({self.telegram_id}) - {self.get_user_type_display()}"

class Message(models.Model):
    MESSAGE_SOURCES = [
        ('web', 'Web Interface'),
        ('telegram', 'Telegram Bot'),
    ]
    
    MESSAGE_DIRECTIONS = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    MESSAGE_TYPES = [
        ('chat', 'Обычное сообщение'),
        ('ai_question', 'ИИ вопрос'),
        ('admin_broadcast', 'Рассылка админа'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    source = models.CharField(max_length=10, choices=MESSAGE_SOURCES)
    direction = models.CharField(max_length=10, choices=MESSAGE_DIRECTIONS)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='chat')
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, blank=True, null=True)
    telegram_message_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source} - {self.direction}: {self.text[:50]}"

class ChatSession(models.Model):
    SESSION_TYPES = [
        ('general', 'Общий чат'),
        ('admission', 'Приемная комиссия'),
        ('ai_chat', 'ИИ чат'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='general')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Сессия {self.telegram_user} - {self.get_session_type_display()}"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('passport', 'Паспорт'),
        ('education_cert', 'Аттестат об образовании'),
        ('photo', 'Фотография'),
        ('medical_cert', 'Медицинская справка'),
        ('military_id', 'Военный билет (для мужчин)'),
        ('other', 'Другое'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file_id = models.CharField(max_length=500)  # Telegram file_id
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.telegram_user} - {self.get_document_type_display()}"

class ApplicantProfile(models.Model):
    telegram_user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    desired_faculty = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Профиль {self.telegram_user}"

class ScrapedContent(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=500)
    content = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-scraped_at']
    
    def __str__(self):
        return f"{self.title} ({self.url})"

class BroadcastMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # Web admin user
    message_text = models.TextField()
    target_user_type = models.CharField(max_length=20, choices=TelegramUser.USER_TYPES, blank=True, null=True)
    target_users = models.ManyToManyField(TelegramUser, blank=True)
    sent_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Рассылка от {self.sender} - {self.message_text[:50]}"