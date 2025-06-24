import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, TelegramUser
import json

logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
channel_layer = get_channel_layer()

async def send_telegram_message(user_id: str, message: str) -> bool:
    """Send message to Telegram user"""
    try:
        await bot.send_message(chat_id=user_id, text=message)
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message to {user_id}: {e}")
        return False

async def handle_telegram_message(update: Update, context: CallbackContext):
    """Handle incoming Telegram messages"""
    try:
        user = update.effective_user
        message = update.message
        
        # Save or update Telegram user
        telegram_user, created = await sync_get_or_create_telegram_user(
            telegram_id=str(user.id),
            defaults={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        )
        
        # Save message to database
        saved_message = await sync_save_message(
            text=message.text,
            source='telegram',
            direction='incoming',
            telegram_user_id=str(user.id),
            telegram_username=user.username,
            telegram_message_id=message.message_id
        )
        
        # Send to WebSocket
        await channel_layer.group_send(
            'chat_chat',
            {
                'type': 'chat_message',
                'message': message.text,
                'source': 'telegram',
                'direction': 'incoming',
                'telegram_user_id': str(user.id),
                'telegram_username': user.username or user.first_name,
                'created_at': saved_message.created_at.isoformat(),
                'message_id': str(saved_message.id)
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling Telegram message: {e}")

def sync_get_or_create_telegram_user(telegram_id, defaults):
    """Sync wrapper for database operations"""
    from django.db import transaction
    
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        created = False
        # Update user info
        for key, value in defaults.items():
            if value:
                setattr(user, key, value)
        user.save()
    except TelegramUser.DoesNotExist:
        user = TelegramUser.objects.create(telegram_id=telegram_id, **defaults)
        created = True
    
    return user, created

def sync_save_message(text, source, direction, telegram_user_id=None, telegram_username=None, telegram_message_id=None):
    """Sync wrapper for saving messages"""
    return Message.objects.create(
        text=text,
        source=source,
        direction=direction,
        telegram_user_id=telegram_user_id,
        telegram_username=telegram_username,
        telegram_message_id=telegram_message_id
    )

# Create application
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

# Add handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))

async def start_telegram_bot():
    """Start the Telegram bot"""
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")

async def stop_telegram_bot():
    """Stop the Telegram bot"""
    try:
        await application.stop()
        logger.info("Telegram bot stopped")
    except Exception as e:
        logger.error(f"Error stopping Telegram bot: {e}")