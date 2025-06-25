import asyncio
import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import Message, TelegramUser, ChatSession, Document, ApplicantProfile
from .services.openai_service import UniversityAIService
import json

logger = logging.getLogger(__name__)

# Initialize bot and services
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
channel_layer = get_channel_layer()
ai_service = UniversityAIService()

# Bot states
USER_STATES = {}

class TelegramBotHandler:
    
    @staticmethod
    async def start_command(update: Update, context: CallbackContext):
        """Handle /start command"""
        user = update.effective_user
        
        # Get or create telegram user
        telegram_user = await sync_to_async(TelegramUser.objects.get_or_create)(
            telegram_id=str(user.id),
            defaults={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        )
        
        welcome_text = (
            "🎓 Добро пожаловать в официальный бот МВЭУ!\n\n"
            "Я помогу вам получить информацию об университете, "
            "подать документы и связаться с приемной комиссией.\n\n"
            "Для начала выберите, кто вы:"
        )
        
        keyboard = [
            [InlineKeyboardButton("👨‍🎓 Абитуриент", callback_data="user_type_applicant")],
            [InlineKeyboardButton("👨‍🎓 Студент", callback_data="user_type_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    @staticmethod
    async def button_handler(update: Update, context: CallbackContext):
        """Handle inline keyboard button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        
        if data.startswith("user_type_"):
            await TelegramBotHandler.handle_user_type_selection(query, data)
        elif data.startswith("applicant_"):
            await TelegramBotHandler.handle_applicant_menu(query, data)
        elif data == "back_to_main":
            await TelegramBotHandler.show_main_menu(query)
        elif data == "back_to_applicant":
            await TelegramBotHandler.show_applicant_menu(query)
    
    @staticmethod
    async def handle_user_type_selection(query, data):
        """Handle user type selection"""
        user_type = data.replace("user_type_", "")
        user_id = str(query.from_user.id)
        
        # Update user type in database
        telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
        telegram_user.user_type = user_type
        await sync_to_async(telegram_user.save)()
        
        if user_type == "applicant":
            await TelegramBotHandler.show_applicant_menu(query)
        elif user_type == "student":
            await TelegramBotHandler.show_student_menu(query)
    
    @staticmethod
    async def show_main_menu(query):
        """Show main menu"""
        text = "Выберите, кто вы:"
        keyboard = [
            [InlineKeyboardButton("👨‍🎓 Абитуриент", callback_data="user_type_applicant")],
            [InlineKeyboardButton("👨‍🎓 Студент", callback_data="user_type_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_applicant_menu(query):
        """Show applicant menu"""
        text = (
            "📚 Меню для абитуриентов\n\n"
            "Выберите нужное действие:"
        )
        
        keyboard = [
            [InlineKeyboardButton("❓ Задать вопрос", callback_data="applicant_ask_question")],
            [InlineKeyboardButton("📄 Отправить документы", callback_data="applicant_send_docs")],
            [InlineKeyboardButton("💬 Связаться с приемной комиссией", callback_data="applicant_contact_admission")],
            [InlineKeyboardButton("↩️ Назад к меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_student_menu(query):
        """Show student menu (placeholder)"""
        text = (
            "👨‍🎓 Меню для студентов\n\n"
            "Функционал для студентов в разработке..."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Назад к меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_applicant_menu(query, data):
        """Handle applicant menu actions"""
        user_id = str(query.from_user.id)
        
        if data == "applicant_ask_question":
            await TelegramBotHandler.start_ai_chat(query)
        elif data == "applicant_send_docs":
            await TelegramBotHandler.show_document_requirements(query)
        elif data == "applicant_upload_docs":
            await TelegramBotHandler.start_document_upload(query)
        elif data == "applicant_contact_admission":
            await TelegramBotHandler.start_admission_chat(query)
        elif data.startswith("doc_type_"):
            await TelegramBotHandler.handle_document_type_selection(query, data)
    
    @staticmethod
    async def start_ai_chat(query):
        """Start AI chat session"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "ai_chat"
        
        text = (
            "🤖 ИИ-помощник активирован!\n\n"
            "Задайте любой вопрос об университете МВЭУ:\n"
            "• Направления подготовки\n"
            "• Условия поступления\n"
            "• Документы для подачи\n"
            "• Контакты и адреса\n"
            "• И многое другое!\n\n"
            "Напишите ваш вопрос..."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Назад к меню абитуриента", callback_data="back_to_applicant")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_document_requirements(query):
        """Show document requirements"""
        text = (
            "📄 Перечень документов для поступления:\n\n"
            "📋 Обязательные документы:\n"
            "1️⃣ Паспорт (копия)\n"
            "2️⃣ Аттестат об образовании (оригинал или копия)\n"
            "3️⃣ Фотографии 3×4 (6 штук)\n"
            "4️⃣ Медицинская справка (форма 086/у)\n"
            "5️⃣ Военный билет (для мужчин)\n\n"
            "📝 Дополнительные документы:\n"
            "• Справка о доходах родителей\n"
            "• Документы об особых правах (если есть)\n"
            "• Результаты ЕГЭ\n\n"
            "Отправьте документы через бота или приходите лично в приемную комиссию."
        )
        
        # Set state for document upload
        user_id = str(query.from_user.id)
        
        keyboard = [
            [InlineKeyboardButton("📤 Отправить документы", callback_data="applicant_upload_docs")],
            [InlineKeyboardButton("↩️ Назад к меню абитуриента", callback_data="back_to_applicant")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def start_admission_chat(query):
        """Start admission office chat"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "admission_chat"
        
        # Create chat session
        telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
        chat_session = await sync_to_async(ChatSession.objects.create)(
            telegram_user=telegram_user,
            session_type='admission'
        )
        
        text = (
            "💬 Подключение к приемной комиссии...\n\n"
            "Вы подключены к чату с приемной комиссией МВЭУ.\n"
            "Ваши сообщения будут переданы сотрудникам приемной комиссии.\n\n"
            "Напишите ваш вопрос или сообщение..."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Завершить чат", callback_data="back_to_applicant")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        
        # Notify web admin about new chat
        await TelegramBotHandler.notify_web_admin_new_chat(telegram_user, chat_session)
    
    @staticmethod
    async def notify_web_admin_new_chat(telegram_user, chat_session):
        """Notify web admin about new chat session"""
        try:
            await channel_layer.group_send(
                'admin_chat',
                {
                    'type': 'new_chat_session',
                    'session_id': str(chat_session.id),
                    'user_info': {
                        'telegram_id': telegram_user.telegram_id,
                        'username': telegram_user.username,
                        'first_name': telegram_user.first_name,
                        'user_type': telegram_user.user_type
                    },
                    'created_at': chat_session.created_at.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error notifying web admin: {e}")
    
    @staticmethod
    async def handle_message(update: Update, context: CallbackContext):
        """Handle regular text messages"""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text
        
        # Get user state
        state = USER_STATES.get(user_id, "")
        
        if state == "ai_chat":
            await TelegramBotHandler.handle_ai_question(update, message_text)
        elif state == "admission_chat":
            await TelegramBotHandler.handle_admission_message(update, message_text)
        elif state == "uploading_docs":
            await TelegramBotHandler.handle_document_info(update, message_text)
        else:
            # Default response
            await update.message.reply_text(
                "Используйте /start для начала работы с ботом."
            )
    
    @staticmethod
    async def handle_ai_question(update: Update, question: str):
        """Handle AI question"""
        user_id = str(update.effective_user.id)
        
        # Send "typing" action
        await bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get AI response
            ai_response = await sync_to_async(ai_service.get_ai_response)(question)
            
            # Save message to database
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            await sync_to_async(Message.objects.create)(
                text=question,
                source='telegram',
                direction='incoming',
                message_type='ai_question',
                telegram_user=telegram_user
            )
            
            await sync_to_async(Message.objects.create)(
                text=ai_response,
                source='telegram',
                direction='outgoing',
                message_type='ai_question',
                telegram_user=telegram_user
            )
            
            # Send response
            keyboard = [
                [InlineKeyboardButton("❓ Задать еще вопрос", callback_data="applicant_ask_question")],
                [InlineKeyboardButton("↩️ Назад к меню", callback_data="back_to_applicant")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(ai_response, reply_markup=reply_markup)
            
            # Clear state to allow new questions
            USER_STATES[user_id] = "ai_chat"
            
        except Exception as e:
            logger.error(f"Error handling AI question: {e}")
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке вашего вопроса. Попробуйте позже."
            )
    
    @staticmethod
    async def handle_admission_message(update: Update, message_text: str):
        """Handle admission office chat message"""
        user_id = str(update.effective_user.id)
        
        try:
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            
            # Save message to database
            message = await sync_to_async(Message.objects.create)(
                text=message_text,
                source='telegram',
                direction='incoming',
                telegram_user=telegram_user
            )
            
            # Send to web admin interface
            await channel_layer.group_send(
                'admin_chat',
                {
                    'type': 'telegram_message',
                    'message': message_text,
                    'source': 'telegram',
                    'direction': 'incoming',
                    'telegram_user_id': user_id,
                    'telegram_username': telegram_user.username or telegram_user.first_name,
                    'created_at': message.created_at.isoformat(),
                    'message_id': str(message.id)
                }
            )
            
            await update.message.reply_text(
                "✅ Ваше сообщение отправлено в приемную комиссию. Ожидайте ответа..."
            )
            
        except Exception as e:
            logger.error(f"Error handling admission message: {e}")
            await update.message.reply_text("Ошибка отправки сообщения.")
    
    @staticmethod
    async def handle_document(update: Update, context: CallbackContext):
        """Handle document upload"""
        user_id = str(update.effective_user.id)
        
        if USER_STATES.get(user_id) != "uploading_docs":
            return
        
        document = update.message.document
        photo = update.message.photo
        
        if document or photo:
            try:
                telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
                
                if document:
                    file_info = document
                    file_id = document.file_id
                    file_name = document.file_name or "document"
                    file_size = document.file_size
                else:  # photo
                    file_info = photo[-1]  # Get highest resolution
                    file_id = photo[-1].file_id
                    file_name = "photo.jpg"
                    file_size = photo[-1].file_size
                
                # Save document info
                doc = await sync_to_async(Document.objects.create)(
                    telegram_user=telegram_user,
                    document_type='other',  # Will be updated when user specifies
                    file_id=file_id,
                    file_name=file_name,
                    file_size=file_size
                )
                
                # Ask for document type
                keyboard = [
                    [InlineKeyboardButton("📄 Паспорт", callback_data=f"doc_type_passport_{doc.id}")],
                    [InlineKeyboardButton("🎓 Аттестат", callback_data=f"doc_type_education_cert_{doc.id}")],
                    [InlineKeyboardButton("📸 Фотография", callback_data=f"doc_type_photo_{doc.id}")],
                    [InlineKeyboardButton("🏥 Медсправка", callback_data=f"doc_type_medical_cert_{doc.id}")],
                    [InlineKeyboardButton("🎖️ Военный билет", callback_data=f"doc_type_military_id_{doc.id}")],
                    [InlineKeyboardButton("📋 Другое", callback_data=f"doc_type_other_{doc.id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ Документ '{file_name}' получен!\n\nУкажите тип документа:",
                    reply_markup=reply_markup
                )
                
            except Exception as e:
                logger.error(f"Error handling document: {e}")
                await update.message.reply_text("Ошибка обработки документа.")

# Setup application
def setup_telegram_application():
    """Setup telegram application with handlers"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", TelegramBotHandler.start_command))
    application.add_handler(CallbackQueryHandler(TelegramBotHandler.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramBotHandler.handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, TelegramBotHandler.handle_document))
    
    return application

# Global application instance
application = setup_telegram_application()

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