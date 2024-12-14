# app/services/rss_service.py

from typing import List, Dict, Optional
import feedparser
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import HTTPException
import asyncio
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

class RSSService:
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (News Summarizer Bot)"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_feeds(self, urls: List[str]) -> List[Dict]:
        """Fetch multiple RSS feeds concurrently."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        tasks = [self.fetch_feed(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {url}: {str(result)}")
                continue
            all_articles.extend(result)
        
        return all_articles

    async def fetch_feed(self, url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed."""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch RSS feed: {url}"
                    )
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries:
                    article = await self._parse_entry(entry, url)
                    if article:
                        articles.append(article)
                
                return articles

        except Exception as e:
            logger.error(f"Error processing feed {url}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing feed: {str(e)}"
            )

    async def fetch_content(self, url: str) -> str:
        """Fetch full article content from URL."""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                content = self._extract_article_content(html)
                return content

        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return None

    def _extract_article_content(self, html: str) -> str:
        """Extract main article content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try common article content selectors
        content_selectors = [
            "article",
            '[role="main"]',
            '.post-content',
            '.article-content',
            '.entry-content',
            '#main-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return content.get_text(separator='\n', strip=True)
        
        # Fallback to body content
        return soup.body.get_text(separator='\n', strip=True) if soup.body else ""

    async def _parse_entry(self, entry, feed_url: str) -> Optional[Dict]:
        """Parse a feed entry into a standardized format."""
        try:
            # Parse publication date
            published = None
            if hasattr(entry, 'published'):
                published = parser.parse(entry.published)
            elif hasattr(entry, 'updated'):
                published = parser.parse(entry.updated)
            
            # Get content
            content = ""
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            
            # Clean content
            if content:
                content = BeautifulSoup(content, 'html.parser').get_text(separator='\n', strip=True)
            
            return {
                'title': entry.title,
                'link': entry.link,
                'content': content,
                'published': published,
                'source_url': feed_url,
                'author': getattr(entry, 'author', None),
                'tags': [tag.term for tag in getattr(entry, 'tags', [])],
            }

        except Exception as e:
            logger.error(f"Error parsing entry from {feed_url}: {str(e)}")
            return None