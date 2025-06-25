import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from ..models import StudentGroup, Schedule, Teacher, Classroom, ScheduleEntry

logger = logging.getLogger(__name__)

class ScheduleService:
    """Service for parsing and managing schedule from raspisanie.mvekspo.ru"""
    
    def __init__(self):
        self.base_url = "https://raspisanie.mvekspo.ru"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def get_groups_data(self) -> Dict:
        """Get groups data from the schedule website"""
        try:
            # Try to get groups from API first
            response = self.session.get(f"{self.api_url}/groups", timeout=10)
            if response.status_code == 200:
                return response.json()
            
            # Fallback to parsing main page
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            # Parse groups from page (this would need to be implemented based on actual page structure)
            # For now, using the data we extracted
            return {
                "1 курс": ["ДБ-241/21", "ДГД-241.1/21", "ДГД-241.2/21", "ДГД-241.3/21", "ДГД-241.4/21", "ДД-241.1/21", "ДД-241/21.Б", "ДД-241.2/21", "ДИС-241.1/21", "ДИС-241.2/21", "ДИС-241.3/21", "ДИС-241.4/21", "ДИС-241.5/21", "ДИС-241/21.Б", "ДИС-241.6/21", "ДНГ-241/21", "ДП-241.1/21", "ДП-241.2/21", "ДП-241.3/21", "ДР-241.1/21", "ДР-241.2/21", "ДР-241.3/21", "ДТГ-241.1/21", "ДТГ-241.2/21", "ДТГ-241.3/21", "ДТД-241/21", "ДЮ-241.1/21", "ДЮ-241.2/21"],
                "2 курс": ["ДБ-232/21", "ДГД-232.1/21", "ДГД-232.2/21", "ДГД-232/2", "ДГД-214/21", "ДГД-232/21", "ДГД-241/2", "ДГД-232/21Б", "ДГД-232.3/21", "ДД-232.1/21", "ДД-232/21Б", "ДД-232.2/21", "ДИС-232.1/21", "ДИС-241.1/2", "ДИС-232.2/21", "ДИС-232.3/21", "ДИС-232.4/21", "ДИС-232.5/21", "ДИС-232/21 Б", "ДИС-232.6/21", "ДИС-241.2/2", "ДИС-232.7/21", "ДК 232.1/21", "ДК-232/21Б", "ДК-232.2/21", "ДНГ-232/21", "ДНГ-241/2", "ДОИС-232/21", "ДОИС-241/2", "ДП-232.1/21", "ДП-232.2/21", "ДП-232.3/21", "ДП-241/2", "ДПО-232/21", "ДР-232.1/21", "ДР-232.2/21", "ДР-241/2", "ДР-232/21н", "ДТГ-232/21", "ДТГ-241/2"],
                "3 курс": ["ДБ-223/21", "ДБ-232/2", "ДД-223.1/21", "ДД-232/2", "ДД-223.2/21", "ДИС-223.1/21", "ДИС-232.2/21", "ДИС-223.3/21", "ДИС-223.4/21", "ДК-223/21", "ДК-232/2", "ДНГ-223/21", "ДП-223.1/21", "ДП-223.2/21", "ДП-223.3/21", "ДП 232/2", "ДПО-223/21", "ДПО-232/2", "ДР-223.1/21", "ДР 232.1/2", "ДР-223.2/21", "ДР 232.2/2", "ДР-223.3/21", "ДР 232.3/2", "ДТГ-223/21", "ДТГ-232/2"],
                "4 курс": ["ДД-214/21", "ДД-214/21Б", "ДД-223/2", "ДИС-214.1/21", "ДИС-223/2", "ДИС-214/21Б", "ДИС-214.2/21", "ДИС-214.3/21", "ДНГ-214/21", "ДНГ-223/2", "ДР-214.1/21", "ДР-223/2", "ДР-214.2/21"]
            }
            
        except Exception as e:
            logger.error(f"Error fetching groups data: {e}")
            return {}
    
    async def get_group_schedule(self, group_name: str, date: datetime = None) -> List[Dict]:
        """Get schedule for specific group"""
        try:
            if date is None:
                date = datetime.now()
            
            # Format date for API
            date_str = date.strftime("%Y-%m-%d")
            
            # Try different API endpoints
            endpoints = [
                f"{self.api_url}/schedule/{group_name}",
                f"{self.api_url}/schedule?group={group_name}&date={date_str}",
                f"{self.base_url}/schedule/{group_name}",
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and data:
                            return data
                        elif isinstance(data, dict) and 'schedule' in data:
                            return data['schedule']
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            # If API fails, return mock schedule data
            return self.generate_mock_schedule(group_name, date)
            
        except Exception as e:
            logger.error(f"Error fetching schedule for group {group_name}: {e}")
            return []
    
    def generate_mock_schedule(self, group_name: str, date: datetime) -> List[Dict]:
        """Generate mock schedule data for demonstration"""
        base_subjects = [
            "Математика", "Информатика", "Физика", "История", 
            "Литература", "Английский язык", "Экономика", "Философия"
        ]
        
        times = [
            "09:00-10:30", "10:40-12:10", "12:20-13:50", 
            "14:40-16:10", "16:20-17:50", "18:00-19:30"
        ]
        
        schedule = []
        weekday = date.weekday()
        
        # Different schedule for different days
        num_lessons = 4 if weekday < 5 else 2  # Less lessons on Friday
        
        for i in range(num_lessons):
            subject = base_subjects[i % len(base_subjects)]
            schedule.append({
                "time": times[i],
                "subject": subject,
                "teacher": f"Преподаватель {i+1}",
                "classroom": f"Ауд. {100 + i}",
                "type": "Лекция" if i % 2 == 0 else "Практика"
            })
        
        return schedule
    
    async def update_schedule_data(self):
        """Update all schedule data in database"""
        try:
            logger.info("Starting schedule data update...")
            
            # Get groups data
            groups_data = await self.get_groups_data()
            
            # Update groups in database
            for course, groups in groups_data.items():
                for group_name in groups:
                    group, created = StudentGroup.objects.get_or_create(
                        name=group_name,
                        defaults={
                            'course': course,
                            'faculty': self.extract_faculty_from_group(group_name),
                            'is_active': True
                        }
                    )
                    if created:
                        logger.info(f"Created new group: {group_name}")
            
            # Update schedule for active groups (limit to avoid overload)
            active_groups = StudentGroup.objects.filter(is_active=True)[:20]  # Limit for demo
            
            for group in active_groups:
                try:
                    # Get schedule for current week
                    today = timezone.now()
                    for days_ahead in range(7):
                        schedule_date = today + timedelta(days=days_ahead)
                        await self.update_group_schedule(group, schedule_date)
                
                except Exception as e:
                    logger.error(f"Error updating schedule for group {group.name}: {e}")
            
            logger.info("Schedule data update completed")
            
        except Exception as e:
            logger.error(f"Error in update_schedule_data: {e}")
    
    async def update_group_schedule(self, group: StudentGroup, date: datetime):
        """Update schedule for specific group and date"""
        try:
            schedule_data = await self.get_group_schedule(group.name, date)
            
            # Clear existing schedule for this date
            ScheduleEntry.objects.filter(
                group=group,
                date=date.date()
            ).delete()
            
            # Create new schedule entries
            for entry_data in schedule_data:
                # Get or create teacher
                teacher_name = entry_data.get('teacher', 'Преподаватель')
                teacher, _ = Teacher.objects.get_or_create(
                    name=teacher_name,
                    defaults={'email': f"{teacher_name.lower().replace(' ', '')}@mveu.ru"}
                )
                
                # Get or create classroom
                classroom_name = entry_data.get('classroom', 'Ауд. 101')
                classroom, _ = Classroom.objects.get_or_create(
                    name=classroom_name,
                    defaults={'capacity': 30, 'building': 'Главный корпус'}
                )
                
                # Create schedule entry
                ScheduleEntry.objects.create(
                    group=group,
                    date=date.date(),
                    time=entry_data.get('time', '09:00-10:30'),
                    subject=entry_data.get('subject', 'Предмет'),
                    teacher=teacher,
                    classroom=classroom,
                    lesson_type=entry_data.get('type', 'Лекция')
                )
            
        except Exception as e:
            logger.error(f"Error updating schedule for {group.name} on {date}: {e}")
    
    def extract_faculty_from_group(self, group_name: str) -> str:
        """Extract faculty from group name"""
        prefixes = {
            'ДБ': 'Факультет бизнеса',
            'ДГД': 'Факультет графического дизайна',
            'ДД': 'Факультет дизайна',
            'ДИС': 'Факультет информационных систем',
            'ДК': 'Факультет культуры',
            'ДНГ': 'Факультет гуманитарных наук',
            'ДОИС': 'Факультет информационной безопасности',
            'ДП': 'Педагогический факультет',
            'ДПО': 'Факультет психологии',
            'ДР': 'Факультет рекламы',
            'ДТГ': 'Технический факультет',
            'ДТД': 'Факультет туризма',
            'ДЮ': 'Юридический факультет'
        }
        
        for prefix, faculty in prefixes.items():
            if group_name.startswith(prefix):
                return faculty
        
        return 'Общий факультет'
    
    async def get_today_schedule(self, group_name: str) -> List[Dict]:
        """Get today's schedule for group"""
        return await self.get_group_schedule(group_name, datetime.now())
    
    async def get_week_schedule(self, group_name: str) -> Dict[str, List[Dict]]:
        """Get week schedule for group"""
        week_schedule = {}
        today = datetime.now()
        
        # Get Monday of current week
        monday = today - timedelta(days=today.weekday())
        
        for i in range(7):
            date = monday + timedelta(days=i)
            day_name = date.strftime("%A")
            day_schedule = await self.get_group_schedule(group_name, date)
            week_schedule[f"{day_name} ({date.strftime('%d.%m')})"] = day_schedule
        
        return week_schedule
    
    async def search_groups(self, query: str) -> List[str]:
        """Search groups by name"""
        groups_data = await self.get_groups_data()
        all_groups = []
        
        for course_groups in groups_data.values():
            all_groups.extend(course_groups)
        
        # Filter groups by query
        matching_groups = [
            group for group in all_groups 
            if query.lower() in group.lower()
        ]
        
        return matching_groups[:10]  # Limit results