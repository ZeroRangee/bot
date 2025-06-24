from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Message, TelegramUser
from .serializers import MessageSerializer, TelegramUserSerializer
import json

def index(request):
    """Main chat interface"""
    return render(request, 'chat/index.html')

@api_view(['GET'])
def get_messages(request):
    """Get recent messages"""
    messages = Message.objects.all()[:50]
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_telegram_users(request):
    """Get list of Telegram users"""
    users = TelegramUser.objects.filter(is_active=True)
    serializer = TelegramUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def send_message(request):
    """Send message via API"""
    try:
        data = request.data
        message_text = data.get('message', '')
        telegram_user_id = data.get('telegram_user_id', '')
        
        if not message_text:
            return Response({'error': 'Message text is required'}, status=400)
        
        # Save message
        message = Message.objects.create(
            text=message_text,
            source='web',
            direction='outgoing',
            telegram_user_id=telegram_user_id
        )
        
        # Send to Telegram if user_id provided
        if telegram_user_id:
            from .telegram_bot import send_telegram_message
            import asyncio
            success = asyncio.run(send_telegram_message(telegram_user_id, message_text))
            if not success:
                return Response({'error': 'Failed to send to Telegram'}, status=500)
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
def telegram_webhook(request):
    """Handle Telegram webhooks"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process webhook data here if needed
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'status': 'method not allowed'}, status=405)