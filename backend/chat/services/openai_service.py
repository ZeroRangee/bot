import openai
from django.conf import settings
from typing import List, Dict
import logging
from ..models import ScrapedContent
from .web_scraper import UniversityWebScraper

logger = logging.getLogger(__name__)

class UniversityAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def get_university_context(self):
        """Get university information from scraped data"""
        # Get recent scraped data
        scraped_content = ScrapedContent.objects.filter(is_active=True)[:10]
        
        if not scraped_content.exists():
            # If no scraped data, scrape fresh data
            self.refresh_university_data()
            scraped_content = ScrapedContent.objects.filter(is_active=True)[:10]
        
        context = []
        for content in scraped_content:
            context.append({
                'url': content.url,
                'title': content.title,
                'content': content.content[:1500]  # Limit content
            })
        
        return context
    
    def refresh_university_data(self):
        """Refresh university data by scraping"""
        try:
            scraper = UniversityWebScraper()
            scraped_data = scraper.scrape_university_info()
            
            # Deactivate old content
            ScrapedContent.objects.filter(is_active=True).update(is_active=False)
            
            # Save new content
            for data in scraped_data:
                ScrapedContent.objects.create(
                    url=data['url'],
                    title=data['title'],
                    content=data['content']
                )
            
            logger.info(f"Refreshed {len(scraped_data)} pages of university data")
        except Exception as e:
            logger.error(f"Error refreshing university data: {e}")
    
    def create_context_prompt(self, university_data: List[Dict], user_question: str) -> str:
        """Create a context-aware prompt using university data"""
        context = "Информация о МВЭУ (Московский Внешкольный Экономический Университет):\n\n"
        
        for data in university_data:
            context += f"Страница: {data['title']}\n"
            context += f"URL: {data['url']}\n"
            context += f"Содержание: {data['content'][:800]}...\n\n"
        
        prompt = f"""
Ты - полезный ассистент для МВЭУ (Московский Внешкольный Экономический Университет).
Используй следующую информацию об университете для точного и полезного ответа на вопросы.

{context}

Вопрос пользователя: {user_question}

Инструкции:
1. Предоставь исчерпывающий ответ, основанный на информации об университете выше
2. Если информации недостаточно в контексте, так и скажи и предложи обратиться в приемную комиссию
3. Отвечай на русском языке
4. Будь дружелюбным и полезным
5. Если вопрос касается поступления, упомяни возможность подачи документов через бота
"""
        return prompt
    
    def get_ai_response(self, user_question: str) -> str:
        """Get AI response for user question"""
        try:
            # Get university context
            university_data = self.get_university_context()
            
            # Create prompt
            prompt = self.create_context_prompt(university_data, user_question)
            
            # Get GPT response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - знающий ассистент для МВЭУ. Предоставляй точную и полезную информацию на основе предоставленного контекста."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "Извините, у меня сейчас проблемы с получением информации. Попробуйте позже или свяжитесь с приемной комиссией."