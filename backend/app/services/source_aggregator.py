# app/services/source_aggregator.py

from typing import List, Dict, Any
import logging
from datetime import datetime
import pytz
from app.services.rss_processor import RSSProcessor

logger = logging.getLogger(__name__)

class SourceAggregator:
    def __init__(self):
        self.rss_processor = RSSProcessor()

    async def aggregate_sources(
        self,
        news_sources: List[str]
    ) -> List[Dict[str, Any]]:
        """Aggregate content from multiple news sources."""
        try:
            # Process RSS feeds
            aggregated_content = await self.rss_processor.process_feeds(
                feed_urls=news_sources
            )
            
            if not aggregated_content.articles:
                logger.warning("No articles found from provided sources")
                return []

            # Log processing results
            logger.info(
                f"Processed {len(aggregated_content.articles)} articles from "
                f"{len(aggregated_content.sources)} sources"
            )
            
            if aggregated_content.failed_sources:
                logger.warning(
                    f"Failed to process {len(aggregated_content.failed_sources)} "
                    f"sources: {aggregated_content.failed_sources}"
                )

            # Format articles for LLM processing
            formatted_articles = []
            for article in aggregated_content.articles:
                formatted_articles.append({
                    'title': article['title'],
                    'content': article['content'],
                    'link': article['source_url'],
                    'published': article['published'],
                    'source': article['source_feed']
                })

            return formatted_articles

        except Exception as e:
            logger.error(f"Error aggregating sources: {str(e)}")
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rss_processor.close()