import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from .telegram_bot import send_telegram_message

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
                telegram_success = await send_telegram_message(telegram_user_id, message_text)
                if not telegram_success:
                    await self.send(text_data=json.dumps({
                        'error': 'Failed to send message to Telegram'
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

    @database_sync_to_async
    def save_message(self, text, source, direction, telegram_user_id=None, telegram_username=None, telegram_message_id=None):
        return Message.objects.create(
            text=text,
            source=source,
            direction=direction,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            telegram_message_id=telegram_message_id
        )