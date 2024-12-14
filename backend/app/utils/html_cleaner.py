from bs4 import BeautifulSoup
import re
from typing import Set

class HTMLCleaner:
    def __init__(self):
        self.unwanted_tags = {
            'script', 'style', 'iframe', 'nav', 'header', 'footer',
            'aside', 'form', 'button', 'noscript'
        }
        self.ad_classes = {
            'ad', 'ads', 'advertisement', 'banner', 'social',
            'share', 'popup', 'modal'
        }

    def clean_html(self, html: str) -> str:
        """Clean HTML content and extract meaningful text"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Remove empty elements
        self._remove_empty_elements(soup)
        
        # Extract text with proper spacing
        text = self._extract_text(soup)
        
        # Clean up whitespace
        text = self._clean_whitespace(text)
        
        return text

    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Remove unwanted HTML elements"""
        # Remove unwanted tags
        for tag in soup.find_all(self.unwanted_tags):
            tag.decompose()
        
        # Remove elements with ad-related classes
        for element in soup.find_all(class_=self._is_ad_class):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str)):
            comment.extract()

    def _is_ad_class(self, classes: Set[str]) -> bool:
        """Check if any class matches ad-related patterns"""
        if not classes:
            return False
        return any(ad_class in class_.lower() for class_ in classes for ad_class in self.ad_classes)

    def _remove_empty_elements(self, soup: BeautifulSoup):
        """Remove elements that contain no useful text"""
        for element in soup.find_all():
            if not element.get_text(strip=True):
                element.decompose()

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract text with proper spacing between elements"""
        # Add newlines for block elements
        for tag in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.append('\n')
        
        # Add extra newline for paragraphs
        for tag in soup.find_all('p'):
            tag.append('\n')
        
        return soup.get_text()

    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace in text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # Remove extra newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()