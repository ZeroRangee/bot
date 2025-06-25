import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class UniversityWebScraper:
    def __init__(self, base_url="https://www.mveu.ru"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': text[:3000],  # Limit content length
                'scraped_at': time.time()
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_university_info(self):
        """Scrape key university information pages"""
        pages_to_scrape = [
            f"{self.base_url}/",
            f"{self.base_url}/abiturientu/",
            f"{self.base_url}/abiturientu/priemnaya-komissiya/",
            f"{self.base_url}/abiturientu/napravleniya-podgotovki/",
            f"{self.base_url}/abiturientu/dokumenty/",
            f"{self.base_url}/contacts/",
            f"{self.base_url}/about/",
        ]
        
        scraped_data = []
        for url in pages_to_scrape:
            try:
                data = self.scrape_page(url)
                if data:
                    scraped_data.append(data)
                time.sleep(1)  # Be respectful to the server
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue
        
        return scraped_data