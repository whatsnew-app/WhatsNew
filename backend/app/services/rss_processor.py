# app/services/rss_processor.py

from typing import List, Dict, Any, Optional
import asyncio
import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from app.schemas.rss import AggregatedContent
import logging
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)

class RSSProcessor:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

    async def process_feeds(
        self,
        feed_urls: List[str],
        hours: int = 1
    ) -> AggregatedContent:
        """Process multiple RSS feeds and aggregate their content."""
        try:
            successful_sources = []
            failed_sources = []
            processed_articles = []

            for url in feed_urls:
                try:
                    # Fetch RSS feed
                    response = await self.client.get(url)
                    response.raise_for_status()
                    
                    # Parse feed
                    feed = feedparser.parse(response.text)
                    if not feed.entries:
                        logger.warning(f"No entries found in feed: {url}")
                        failed_sources.append(url)
                        continue

                    # Process each entry
                    for entry in feed.entries:
                        try:
                            # Get published date
                            published = self._parse_date(
                                entry.get('published', entry.get('updated'))
                            )
                            
                            # Skip if too old
                            if not self._is_recent(published, hours):
                                continue

                            # Get full content
                            content = await self._get_article_content(
                                entry.get('link'),
                                entry.get('description', '')
                            )

                            processed_articles.append({
                                'title': entry.get('title', '').strip(),
                                'content': content,
                                'source_url': entry.get('link', url),
                                'published': published.isoformat(),
                                'source_feed': url
                            })

                        except Exception as e:
                            logger.error(f"Error processing entry from {url}: {str(e)}")
                            continue

                    successful_sources.append(url)

                except Exception as e:
                    logger.error(f"Error processing feed {url}: {str(e)}")
                    failed_sources.append(url)
                    continue

            # Sort by published date
            processed_articles.sort(
                key=lambda x: x['published'],
                reverse=True
            )

            return AggregatedContent(
                articles=processed_articles,
                sources=successful_sources,
                failed_sources=failed_sources,
                metadata={
                    'total_articles': len(processed_articles),
                    'successful_sources': len(successful_sources),
                    'failed_sources': len(failed_sources),
                    'processing_time': datetime.now(pytz.UTC).isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error in feed processing: {str(e)}")
            raise

    async def _get_article_content(
        self,
        url: Optional[str],
        fallback_content: str
    ) -> str:
        """Fetch and extract article content."""
        if not url:
            return self._clean_html(fallback_content)

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup.find_all(['script', 'style', 'iframe', 'nav', 'footer']):
                tag.decompose()

            # Try to find the main content
            content = ''
            
            # Look for article content in common containers
            article = soup.find('article')
            if article:
                content = article.get_text(separator=' ', strip=True)
            else:
                # Try common content div classes/ids
                for selector in ['.article-body', '#article-body', '.story-body', '.content-body']:
                    content_div = soup.select_one(selector)
                    if content_div:
                        content = content_div.get_text(separator=' ', strip=True)
                        break

            # Fallback to description if no content found
            if not content:
                content = self._clean_html(fallback_content)

            return content

        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {str(e)}")
            return self._clean_html(fallback_content)

    def _clean_html(self, content: str) -> str:
        """Clean HTML content."""
        if not content:
            return ""

        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get text with proper spacing
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime object."""
        if not date_str:
            return datetime.now(pytz.UTC)

        try:
            # Try parsing with feedparser's date handler
            parsed = feedparser._parse_date(date_str)
            if parsed:
                dt = datetime(*parsed[:6])
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=pytz.UTC)
                return dt
        except:
            pass

        # Fallback to current time
        return datetime.now(pytz.UTC)

    def _is_recent(self, dt: datetime, hours: int = 1) -> bool:
        """Check if datetime is within specified hours from now."""
        now = datetime.now(pytz.UTC)
        cutoff = now - timedelta(hours=hours)
        return dt >= cutoff

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()