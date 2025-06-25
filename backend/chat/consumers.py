import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, TelegramUser
from .telegram_bot import bot

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat'
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_text = text_data_json['message']
            telegram_user_id = text_data_json.get('telegram_user_id', '')

            # Save message to database
            message = await self.save_message(
                text=message_text,
                source='web',
                direction='outgoing',
                telegram_user_id=telegram_user_id
            )

            # Send message to Telegram if telegram_user_id is provided
            if telegram_user_id:
                try:
                    await bot.send_message(chat_id=telegram_user_id, text=message_text)
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        'error': f'Failed to send message to Telegram: {str(e)}'
                    }))
                    return

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'source': 'web',
                    'direction': 'outgoing',
                    'telegram_user_id': telegram_user_id,
                    'created_at': message.created_at.isoformat(),
                    'message_id': str(message.id)
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Error processing message: {str(e)}'
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'source': event['source'],
            'direction': event['direction'],
            'telegram_user_id': event.get('telegram_user_id', ''),
            'telegram_username': event.get('telegram_username', ''),
            'created_at': event['created_at'],
            'message_id': event['message_id']
        }))

    # Handle admin chat specific events
    async def new_chat_session(self, event):
        """Handle new chat session notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_chat_session',
            'session_id': event['session_id'],
            'user_info': event['user_info'],
            'created_at': event['created_at']
        }))

    async def telegram_message(self, event):
        """Handle telegram message for admin interface"""
        await self.send(text_data=json.dumps({
            'type': 'telegram_message',
            'message': event['message'],
            'source': event['source'],
            'direction': event['direction'],
            'telegram_user_id': event['telegram_user_id'],
            'telegram_username': event['telegram_username'],
            'created_at': event['created_at'],
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_message(self, text, source, direction, telegram_user_id=None, telegram_username=None, telegram_message_id=None):
        telegram_user = None
        if telegram_user_id:
            try:
                telegram_user = TelegramUser.objects.get(telegram_id=telegram_user_id)
            except TelegramUser.DoesNotExist:
                pass
        
        return Message.objects.create(
            text=text,
            source=source,
            direction=direction,
            telegram_user=telegram_user,
            telegram_message_id=telegram_message_id
        )

class AdminChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join admin chat group
        await self.channel_layer.group_add(
            'admin_chat',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave admin chat group
        await self.channel_layer.group_discard(
            'admin_chat',
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle admin messages if needed
        pass

    async def new_chat_session(self, event):
        """Forward new chat session to admin"""
        await self.send(text_data=json.dumps(event))

    async def telegram_message(self, event):
        """Forward telegram messages to admin"""
        await self.send(text_data=json.dumps(event))