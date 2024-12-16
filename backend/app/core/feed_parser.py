# app/core/feed_parser.py

from typing import Optional, Dict, List, Any
import feedparser
from datetime import datetime, timedelta
import pytz
from urllib.parse import urlparse
import logging
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class FeedParser:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def parse_feed(self, url: str) -> Dict[str, Any]:
        """Parse RSS feed and return structured content."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            if not feed.entries:
                logger.warning(f"No entries found in feed: {url}")
                return None
                
            return self._process_feed(feed, url)
            
        except Exception as e:
            logger.error(f"Error parsing feed {url}: {str(e)}")
            return None
            
    def _process_feed(self, feed: feedparser.FeedParserDict, url: str) -> Dict[str, Any]:
        """Process feed entries and extract relevant information."""
        processed_entries = []
        
        for entry in feed.entries:
            try:
                published = self._parse_date(entry.get('published', entry.get('updated')))
                if not self._is_recent(published):
                    continue
                    
                content = self._extract_content(entry)
                processed_entries.append({
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', ''),
                    'description': entry.get('summary', '').strip(),
                    'content': content,
                    'published': published.isoformat(),
                    'author': entry.get('author', ''),
                    'categories': [tag.term for tag in entry.get('tags', [])]
                })
                
            except Exception as e:
                logger.error(f"Error processing entry in {url}: {str(e)}")
                continue
                
        return {
            'title': feed.feed.get('title', ''),
            'link': feed.feed.get('link', url),
            'description': feed.feed.get('description', ''),
            'items': processed_entries,
            'last_updated': datetime.now(pytz.UTC).isoformat()
        }
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime object."""
        if not date_str:
            return datetime.now(pytz.UTC)
        try:
            dt = date_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            return dt
        except Exception:
            return datetime.now(pytz.UTC)
    
    def _is_recent(self, dt: datetime, hours: int = 1) -> bool:
        """Check if datetime is within specified hours from now."""
        now = datetime.now(pytz.UTC)
        cutoff = now - timedelta(hours=hours)
        return dt >= cutoff
    
    def _extract_content(self, entry: Dict[str, Any]) -> str:
        """Extract and clean content from feed entry."""
        content = ''
        
        # Try different content fields
        if 'content' in entry:
            content = entry.content[0].value
        elif 'description' in entry:
            content = entry.description
        elif 'summary' in entry:
            content = entry.summary
            
        # Clean HTML if present
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
            
        return content.strip()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()