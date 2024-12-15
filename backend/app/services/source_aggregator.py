from typing import List, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.rss_service import RSSService

class SourceAggregator:
    def __init__(self):
        self.rss_service = RSSService()

    async def aggregate_sources(
        self,
        sources: List[str],
        hours_back: int = 24
    ) -> List[Dict]:
        """Aggregate content from multiple RSS sources"""
        all_articles = []
        cutoff_time = datetime.utcnow().replace(tzinfo=None)  # Ensure naive datetime
        cutoff_time = cutoff_time - timedelta(hours=hours_back)

        async with self.rss_service as service:
            for source_url in sources:
                try:
                    articles = await service.fetch_feed(source_url)
                    
                    # Filter articles by date and fetch full content
                    for article in articles:
                        pub_date = article['published']
                        if pub_date:
                            # Convert to naive datetime if it has timezone
                            if pub_date.tzinfo:
                                pub_date = pub_date.astimezone().replace(tzinfo=None)
                            
                            if pub_date > cutoff_time:
                                # Fetch full content if summary is too short
                                if len(article['content']) < 500:
                                    article['content'] = await service.fetch_content(
                                        article['link']
                                    )
                                all_articles.append(article)

                except HTTPException as e:
                    # Log error but continue with other sources
                    print(f"Error processing {source_url}: {str(e)}")
                    continue

        return self._deduplicate_articles(all_articles)

    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = {}
        
        for article in articles:
            title_key = self._normalize_title(article['title'])
            
            if title_key not in unique_articles:
                unique_articles[title_key] = article
            else:
                # Keep the longer content version
                if len(article['content']) > len(unique_articles[title_key]['content']):
                    unique_articles[title_key] = article

        return list(unique_articles.values())

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        return ''.join(c.lower() for c in title if c.isalnum())