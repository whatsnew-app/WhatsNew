from typing import List, Dict, Optional
from datetime import datetime
import feedparser
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fastapi import HTTPException

class RSSService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_feed(self, url: str) -> List[Dict]:
        try:
            response = await self.client.get(url)
            feed = feedparser.parse(response.text)
            
            if feed.bozo:  # Feed parsing error
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid RSS feed: {url}"
                )

            articles = []
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': self._parse_date(entry.get('published', '')),
                    'summary': entry.get('summary', ''),
                    'content': self._get_content(entry),
                    'source_url': url
                }
                articles.append(article)
            
            return articles

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error fetching RSS feed: {str(e)}"
            )

    async def fetch_content(self, url: str) -> str:
        """Fetch full article content from URL"""
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()
            
            # Find main content (customize based on common website structures)
            content = soup.find('article') or soup.find(class_=['content', 'article', 'post'])
            
            if content:
                return content.get_text(separator='\n', strip=True)
            return soup.get_text(separator='\n', strip=True)

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error fetching article content: {str(e)}"
            )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats to datetime"""
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                return datetime.utcnow()

    def _get_content(self, entry) -> str:
        """Extract content from feed entry"""
        if hasattr(entry, 'content'):
            return entry.content[0].value
        return entry.get('summary', '')

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()