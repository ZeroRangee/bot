from django.apps import AppConfig
import threading
import asyncio
import logging

logger = logging.getLogger(__name__)

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    
    def ready(self):
        # Start Telegram bot in a separate thread
        if not hasattr(self, '_bot_started'):
            self._bot_started = True
            self.start_telegram_bot()
    
    def start_telegram_bot(self):
        """Start the Telegram bot in a separate thread"""
        def run_bot():
            try:
                from .telegram_bot import start_telegram_bot
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(start_telegram_bot())
            except Exception as e:
                logger.error(f"Error starting Telegram bot: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Telegram bot thread started")