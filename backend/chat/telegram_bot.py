import asyncio
import logging
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, CallbackContext
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import Message, TelegramUser, ChatSession, Document, ApplicantProfile, StudentProfile, StudentGroup
from .services.openai_service import UniversityAIService
from .services.schedule_service import ScheduleService
import json

logger = logging.getLogger(__name__)

# Initialize bot and services
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
channel_layer = get_channel_layer()
ai_service = UniversityAIService()
schedule_service = ScheduleService()

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
        elif data.startswith("student_"):
            await TelegramBotHandler.handle_student_menu(query, data)
        elif data == "back_to_main":
            await TelegramBotHandler.show_main_menu(query)
        elif data == "back_to_applicant":
            await TelegramBotHandler.show_applicant_menu(query)
        elif data == "back_to_student":
            await TelegramBotHandler.show_student_menu(query)
    
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
        """Show student menu"""
        user_id = str(query.from_user.id)
        
        # Get student profile if exists
        try:
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            student_profile = await sync_to_async(
                lambda: getattr(telegram_user, 'studentprofile', None)
            )()
        except:
            student_profile = None
        
        if student_profile and student_profile.group:
            group_info = f"Группа: {student_profile.group.name}"
        else:
            group_info = "Группа не указана"
        
        text = (
            f"🎓 Меню для студентов\n\n"
            f"👤 {group_info}\n\n"
            f"Выберите нужное действие:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📅 Мое расписание", callback_data="student_my_schedule")],
            [InlineKeyboardButton("🔍 Найти расписание группы", callback_data="student_search_schedule")],
            [InlineKeyboardButton("📊 Расписание на сегодня", callback_data="student_today_schedule")],
            [InlineKeyboardButton("📋 Расписание на неделю", callback_data="student_week_schedule")],
            [InlineKeyboardButton("⚙️ Настроить группу", callback_data="student_set_group")],
            [InlineKeyboardButton("❓ Задать вопрос", callback_data="student_ask_question")],
            [InlineKeyboardButton("↩️ Назад к меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_student_menu(query, data):
        """Handle student menu actions"""
        user_id = str(query.from_user.id)
        
        if data == "student_my_schedule":
            await TelegramBotHandler.show_my_schedule(query)
        elif data == "student_search_schedule":
            await TelegramBotHandler.start_schedule_search(query)
        elif data == "student_today_schedule":
            await TelegramBotHandler.show_today_schedule(query)
        elif data == "student_week_schedule":
            await TelegramBotHandler.show_week_schedule(query)
        elif data == "student_set_group":
            await TelegramBotHandler.start_group_setup(query)
        elif data == "student_ask_question":
            await TelegramBotHandler.start_ai_chat_student(query)
        elif data.startswith("select_group_"):
            group_name = data.replace("select_group_", "").replace("_", "/")
            await TelegramBotHandler.set_student_group(query, group_name)
        elif data.startswith("schedule_group_"):
            group_name = data.replace("schedule_group_", "").replace("_", "/")
            await TelegramBotHandler.show_group_schedule(query, group_name)
    
    @staticmethod
    async def show_my_schedule(query):
        """Show student's personal schedule"""
        user_id = str(query.from_user.id)
        
        try:
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            student_profile = await sync_to_async(
                lambda: getattr(telegram_user, 'studentprofile', None)
            )()
            
            if not student_profile or not student_profile.group:
                text = (
                    "📅 Мое расписание\n\n"
                    "⚠️ Группа не настроена.\n"
                    "Нажмите 'Настроить группу' для выбора вашей группы."
                )
                keyboard = [
                    [InlineKeyboardButton("⚙️ Настроить группу", callback_data="student_set_group")],
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ]
            else:
                # Get today's schedule
                schedule = await schedule_service.get_today_schedule(student_profile.group.name)
                
                text = f"📅 Расписание группы {student_profile.group.name}\n"
                text += f"📆 {datetime.now().strftime('%d.%m.%Y (%A)')}\n\n"
                
                if schedule:
                    for i, lesson in enumerate(schedule, 1):
                        text += f"{i}. {lesson['time']}\n"
                        text += f"   📚 {lesson['subject']}\n"
                        text += f"   👨‍🏫 {lesson['teacher']}\n"
                        text += f"   🏢 {lesson['classroom']}\n"
                        text += f"   📝 {lesson.get('type', 'Лекция')}\n\n"
                else:
                    text += "📭 На сегодня занятий нет"
                
                keyboard = [
                    [InlineKeyboardButton("📋 Неделя", callback_data="student_week_schedule")],
                    [InlineKeyboardButton("🔄 Обновить", callback_data="student_my_schedule")],
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in show_my_schedule: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения расписания. Попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ])
            )
    
    @staticmethod
    async def start_schedule_search(query):
        """Start schedule search process"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "searching_schedule"
        
        text = (
            "🔍 Поиск расписания группы\n\n"
            "Введите название группы или часть названия:\n"
            "Например: ДИС-241, ДД-232, ДБ-223\n\n"
            "💡 Доступные факультеты:\n"
            "• ДИС - Информационные системы\n"
            "• ДД - Дизайн\n"
            "• ДБ - Бизнес\n"
            "• ДП - Педагогический\n"
            "• ДР - Реклама\n"
            "• ДЮ - Юридический\n"
            "И другие..."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_today_schedule(query):
        """Show today's schedule for all groups"""
        text = (
            "📊 Расписание на сегодня\n\n"
            "Выберите группу для просмотра расписания:"
        )
        
        # Get some sample groups
        groups = ["ДИС-241.1/21", "ДД-232.1/21", "ДБ-223/21", "ДП-223.1/21"]
        
        keyboard = []
        for group in groups:
            keyboard.append([
                InlineKeyboardButton(f"📅 {group}", callback_data=f"schedule_group_{group.replace('/', '_')}")
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def show_week_schedule(query):
        """Show week schedule for student's group"""
        user_id = str(query.from_user.id)
        
        try:
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            student_profile = await sync_to_async(
                lambda: getattr(telegram_user, 'studentprofile', None)
            )()
            
            if not student_profile or not student_profile.group:
                text = "⚠️ Группа не настроена. Настройте группу для просмотра расписания."
                keyboard = [
                    [InlineKeyboardButton("⚙️ Настроить группу", callback_data="student_set_group")],
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ]
            else:
                # Get week schedule
                week_schedule = await schedule_service.get_week_schedule(student_profile.group.name)
                
                text = f"📋 Расписание на неделю\n"
                text += f"👥 Группа: {student_profile.group.name}\n\n"
                
                for day, lessons in week_schedule.items():
                    text += f"📅 {day}\n"
                    if lessons:
                        for lesson in lessons:
                            text += f"  {lesson['time']} - {lesson['subject']}\n"
                    else:
                        text += "  📭 Занятий нет\n"
                    text += "\n"
                
                keyboard = [
                    [InlineKeyboardButton("📅 Сегодня", callback_data="student_my_schedule")],
                    [InlineKeyboardButton("🔄 Обновить", callback_data="student_week_schedule")],
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in show_week_schedule: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения расписания.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ])
            )
    
    @staticmethod
    async def start_group_setup(query):
        """Start group setup process"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "setting_group"
        
        text = (
            "⚙️ Настройка группы\n\n"
            "Выберите курс:"
        )
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ 1 курс", callback_data="course_1")],
            [InlineKeyboardButton("2️⃣ 2 курс", callback_data="course_2")],
            [InlineKeyboardButton("3️⃣ 3 курс", callback_data="course_3")],
            [InlineKeyboardButton("4️⃣ 4 курс", callback_data="course_4")],
            [InlineKeyboardButton("🔍 Поиск по названию", callback_data="search_group")],
            [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    
    @staticmethod
    async def set_student_group(query, group_name):
        """Set student's group"""
        user_id = str(query.from_user.id)
        
        try:
            # Get or create student group
            group = await sync_to_async(StudentGroup.objects.get_or_create)(
                name=group_name,
                defaults={
                    'course': '1 курс',  # Default, will be updated
                    'faculty': schedule_service.extract_faculty_from_group(group_name),
                    'is_active': True
                }
            )
            group = group[0]
            
            # Get or create telegram user
            telegram_user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
            
            # Get or create student profile
            student_profile, created = await sync_to_async(StudentProfile.objects.get_or_create)(
                telegram_user=telegram_user,
                defaults={'group': group}
            )
            
            if not created:
                student_profile.group = group
                await sync_to_async(student_profile.save)()
            
            text = (
                f"✅ Группа установлена!\n\n"
                f"👥 Ваша группа: {group_name}\n"
                f"🏫 Факультет: {group.faculty}\n\n"
                f"Теперь вы можете просматривать расписание вашей группы."
            )
            
            keyboard = [
                [InlineKeyboardButton("📅 Мое расписание", callback_data="student_my_schedule")],
                [InlineKeyboardButton("📋 Неделя", callback_data="student_week_schedule")],
                [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error setting student group: {e}")
            await query.edit_message_text(
                "❌ Ошибка установки группы. Попробуйте еще раз.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Назад", callback_data="back_to_student")]
                ])
            )
    
    @staticmethod
    async def show_group_schedule(query, group_name):
        """Show schedule for specific group"""
        try:
            schedule = await schedule_service.get_today_schedule(group_name)
            
            text = f"📅 Расписание группы {group_name}\n"
            text += f"📆 {datetime.now().strftime('%d.%m.%Y (%A)')}\n\n"
            
            if schedule:
                for i, lesson in enumerate(schedule, 1):
                    text += f"{i}. {lesson['time']}\n"
                    text += f"   📚 {lesson['subject']}\n"
                    text += f"   👨‍🏫 {lesson['teacher']}\n"
                    text += f"   🏢 {lesson['classroom']}\n"
                    text += f"   📝 {lesson.get('type', 'Лекция')}\n\n"
            else:
                text += "📭 На сегодня занятий нет"
            
            keyboard = [
                [InlineKeyboardButton("📋 Неделя", callback_data=f"week_schedule_{group_name.replace('/', '_')}")],
                [InlineKeyboardButton("⚙️ Выбрать как мою группу", callback_data=f"select_group_{group_name.replace('/', '_')}")],
                [InlineKeyboardButton("↩️ Назад", callback_data="student_today_schedule")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing group schedule: {e}")
            await query.edit_message_text(
                "❌ Ошибка получения расписания группы.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Назад", callback_data="student_today_schedule")]
                ])
            )
    
    @staticmethod
    async def start_ai_chat_student(query):
        """Start AI chat for students"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "ai_chat_student"
        
        text = (
            "🤖 ИИ-помощник для студентов\n\n"
            "Я могу помочь с вопросами о:\n"
            "📅 Расписании занятий\n"
            "📚 Учебных дисциплинах\n"
            "🏫 Университете и факультетах\n"
            "📝 Академических вопросах\n"
            "🎓 Студенческой жизни\n\n"
            "Задайте любой вопрос..."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Назад к меню студента", callback_data="back_to_student")]
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
    async def start_document_upload(query):
        """Start document upload process"""
        user_id = str(query.from_user.id)
        USER_STATES[user_id] = "uploading_docs"
        
        upload_text = (
            "📤 Загрузка документов\n\n"
            "Отправьте ваши документы по одному.\n"
            "Поддерживаются: фото, PDF, DOC, DOCX\n\n"
            "После отправки каждого документа укажите его тип."
        )
        
        keyboard = [
            [InlineKeyboardButton("↩️ Назад к меню абитуриента", callback_data="back_to_applicant")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=upload_text, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_document_type_selection(query, data):
        """Handle document type selection"""
        parts = data.split("_")
        doc_type = parts[2]
        doc_id = parts[3]
        
        try:
            # Update document type
            document = await sync_to_async(Document.objects.get)(id=doc_id)
            document.document_type = doc_type
            await sync_to_async(document.save)()
            
            doc_type_names = {
                'passport': 'Паспорт',
                'education': 'Аттестат об образовании',
                'photo': 'Фотография',
                'medical': 'Медицинская справка',
                'military': 'Военный билет',
                'other': 'Другое'
            }
            
            type_name = doc_type_names.get(doc_type, 'Документ')
            
            await query.edit_message_text(
                f"✅ Документ сохранен как: {type_name}\n\n"
                f"Можете отправить следующий документ или вернуться в меню.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ Назад к меню абитуриента", callback_data="back_to_applicant")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Error updating document type: {e}")
            await query.edit_message_text("Ошибка обновления типа документа.")
    
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