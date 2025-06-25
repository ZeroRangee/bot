from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message, TelegramUser, ChatSession, Document, ApplicantProfile, BroadcastMessage, ScrapedContent, StudentGroup, StudentProfile, Schedule, ScheduleEntry
from .serializers import MessageSerializer, TelegramUserSerializer, DocumentSerializer, ChatSessionSerializer, StudentGroupSerializer, ScheduleEntrySerializer
from .services.openai_service import UniversityAIService
from .services.schedule_service import ScheduleService
import json
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

def index(request):
    """Main chat interface"""
    return render(request, 'chat/index.html')

@staff_member_required
def admin_chat(request):
    """Admin chat interface"""
    return render(request, 'chat/admin_chat.html')

@api_view(['GET'])
def get_messages(request):
    """Get recent messages"""
    session_id = request.GET.get('session_id')
    telegram_user_id = request.GET.get('telegram_user_id')
    
    messages = Message.objects.all()
    
    if session_id:
        messages = messages.filter(telegram_user__chatsession__id=session_id)
    elif telegram_user_id:
        messages = messages.filter(telegram_user__telegram_id=telegram_user_id)
    
    messages = messages[:50]
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_telegram_users(request):
    """Get list of Telegram users"""
    users = TelegramUser.objects.filter(is_active=True)
    serializer = TelegramUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_sessions(request):
    """Get active chat sessions for admin"""
    sessions = ChatSession.objects.filter(
        is_active=True,
        session_type='admission'
    ).select_related('telegram_user').order_by('-updated_at')
    
    serializer = ChatSessionSerializer(sessions, many=True)
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
        telegram_user = None
        if telegram_user_id:
            try:
                telegram_user = TelegramUser.objects.get(telegram_id=telegram_user_id)
            except TelegramUser.DoesNotExist:
                pass
        
        message = Message.objects.create(
            text=message_text,
            source='web',
            direction='outgoing',
            telegram_user=telegram_user
        )
        
        # Send to Telegram if user_id provided
        if telegram_user_id:
            from .telegram_bot import bot
            import asyncio
            try:
                asyncio.create_task(bot.send_message(chat_id=telegram_user_id, text=message_text))
            except Exception as e:
                return Response({'error': f'Failed to send to Telegram: {str(e)}'}, status=500)
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_admin_message(request):
    """Send message from admin to telegram user"""
    try:
        data = request.data
        message_text = data.get('message', '')
        telegram_user_id = data.get('telegram_user_id', '')
        
        if not message_text or not telegram_user_id:
            return Response({'error': 'Message and user ID are required'}, status=400)
        
        telegram_user = TelegramUser.objects.get(telegram_id=telegram_user_id)
        
        # Save message to database
        message = Message.objects.create(
            text=message_text,
            source='web',
            direction='outgoing',
            telegram_user=telegram_user
        )
        
        # Send to Telegram
        from .telegram_bot import bot
        import asyncio
        asyncio.create_task(bot.send_message(chat_id=telegram_user_id, text=message_text))
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)
        
    except TelegramUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def broadcast_message(request):
    """Broadcast message to multiple users"""
    try:
        data = request.data
        message_text = data.get('message', '')
        target_user_type = data.get('user_type', '')
        target_user_ids = data.get('user_ids', [])
        
        if not message_text:
            return Response({'error': 'Message text is required'}, status=400)
        
        # Create broadcast record
        broadcast = BroadcastMessage.objects.create(
            sender=request.user,
            message_text=message_text,
            target_user_type=target_user_type if target_user_type else None
        )
        
        # Get target users
        target_users = TelegramUser.objects.filter(is_active=True)
        
        if target_user_type:
            target_users = target_users.filter(user_type=target_user_type)
        elif target_user_ids:
            target_users = target_users.filter(telegram_id__in=target_user_ids)
        
        # Add to broadcast
        broadcast.target_users.set(target_users)
        
        # Send messages
        from .telegram_bot import bot
        import asyncio
        sent_count = 0
        
        async def send_broadcasts():
            nonlocal sent_count
            for user in target_users:
                try:
                    await bot.send_message(chat_id=user.telegram_id, text=message_text)
                    
                    # Save individual message
                    Message.objects.create(
                        text=message_text,
                        source='web',
                        direction='outgoing',
                        message_type='admin_broadcast',
                        telegram_user=user
                    )
                    sent_count += 1
                except Exception as e:
                    print(f"Failed to send to {user.telegram_id}: {e}")
            
            # Update sent count
            broadcast.sent_count = sent_count
            broadcast.save()
        
        asyncio.create_task(send_broadcasts())
        
        return Response({
            'message': f'Broadcasting to {target_users.count()} users',
            'broadcast_id': str(broadcast.id)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_documents_stats(request):
    """Get documents statistics"""
    try:
        # Basic stats
        total_documents = Document.objects.count()
        total_applicants = TelegramUser.objects.filter(user_type='applicant').count()
        
        # Documents by type
        doc_types = Document.objects.values('document_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Documents by school (from applicant profiles)
        schools_stats = ApplicantProfile.objects.exclude(
            school_name__isnull=True
        ).exclude(
            school_name__exact=''
        ).values('school_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_docs = Document.objects.filter(created_at__gte=week_ago).count()
        recent_applicants = TelegramUser.objects.filter(
            user_type='applicant',
            created_at__gte=week_ago
        ).count()
        
        return Response({
            'total_documents': total_documents,
            'total_applicants': total_applicants,
            'documents_by_type': list(doc_types),
            'top_schools': list(schools_stats),
            'recent_activity': {
                'documents': recent_docs,
                'new_applicants': recent_applicants
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_user_documents(request, telegram_user_id):
    """Get documents for specific user"""
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_user_id)
        documents = Document.objects.filter(telegram_user=user)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    except TelegramUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
def ai_chat_api(request):
    """AI chat API endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            
            if not question:
                return JsonResponse({'error': 'Question is required'}, status=400)
            
            ai_service = UniversityAIService()
            response = ai_service.get_ai_response(question)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

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

@api_view(['GET'])
def get_student_groups(request):
    """Get list of student groups"""
    try:
        groups = StudentGroup.objects.filter(is_active=True).order_by('name')
        serializer = StudentGroupSerializer(groups, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
async def get_group_schedule(request, group_name):
    """Get schedule for specific group"""
    try:
        from datetime import datetime
        
        # Get date parameter or use today
        date_str = request.GET.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.now()
        
        # Get schedule from service
        schedule_service = ScheduleService()
        schedule_data = await schedule_service.get_group_schedule(group_name, date)
        
        return Response({
            'group': group_name,
            'date': date.strftime('%Y-%m-%d'),
            'schedule': schedule_data
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
async def search_groups(request):
    """Search groups by query"""
    try:
        query = request.data.get('query', '')
        
        if not query:
            return Response({'error': 'Query parameter is required'}, status=400)
        
        # Search groups
        schedule_service = ScheduleService()
        matching_groups = await schedule_service.search_groups(query)
        
        return Response({
            'query': query,
            'groups': matching_groups
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_schedule_stats(request):
    """Get schedule statistics"""
    try:
        # Basic stats
        total_groups = StudentGroup.objects.filter(is_active=True).count()
        total_students = StudentProfile.objects.count()
        
        # Groups by faculty
        faculty_stats = StudentGroup.objects.filter(is_active=True).values('faculty').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Groups by course
        course_stats = StudentGroup.objects.filter(is_active=True).values('course').annotate(
            count=Count('id')
        ).order_by('course')
        
        return Response({
            'total_groups': total_groups,
            'total_students': total_students,
            'faculty_stats': list(faculty_stats),
            'course_stats': list(course_stats)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def update_schedule_data(request):
    """Update schedule data from external source"""
    try:
        schedule_service = ScheduleService()
        
        # Run update in background (in production, use Celery)
        import asyncio
        asyncio.create_task(schedule_service.update_schedule_data())
        
        return Response({
            'message': 'Schedule update started',
            'status': 'success'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)