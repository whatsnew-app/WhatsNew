# app/services/llm_service.py

from typing import Dict, List, Optional, Any
import openai
import anthropic
import httpx
import json
from fastapi import HTTPException
from app.models.ai_config import LLMConfig, LLMProvider
from app.schemas.ai_config import LLMConfig as LLMConfigSchema
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._setup_client()

    def _setup_client(self):
        """Initialize the appropriate LLM client based on provider"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self.client = openai.Client(api_key=self.config.api_key)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
            elif self.config.provider == LLMProvider.CUSTOM:
                self.client = httpx.AsyncClient(
                    base_url=self.config.endpoint_url,
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=60.0
                )
        except Exception as e:
            logger.error(f"Error setting up LLM client: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LLM service: {str(e)}"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_content(
        self,
        articles: List[Dict],
        prompt: str,
        template: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using the configured LLM with retry logic"""
        try:
            # Prepare input for the LLM
            context = self._prepare_context(articles)
            full_prompt = self._prepare_prompt(context, prompt, template)
            
            # Validate input length
            if len(full_prompt) > self.config.parameters.get("max_input_length", 4000):
                context = self._truncate_context(context)
                full_prompt = self._prepare_prompt(context, prompt, template)

            # Generate content using appropriate provider
            start_time = datetime.utcnow()
            
            if self.config.provider == LLMProvider.OPENAI:
                result = await self._generate_with_openai(full_prompt, max_tokens)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                result = await self._generate_with_anthropic(full_prompt, max_tokens)
            elif self.config.provider == LLMProvider.CUSTOM:
                result = await self._generate_with_custom(full_prompt, max_tokens)
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add performance metrics
            result["metadata"]["generation_time"] = generation_time
            result["metadata"]["prompt_length"] = len(full_prompt)
            
            return result

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {str(e)}"
            )

    def _prepare_context(self, articles: List[Dict]) -> str:
        """Prepare context from articles for the LLM"""
        context_parts = []
        total_length = 0
        max_length = self.config.parameters.get("max_context_length", 3000)
        
        for article in sorted(articles, key=lambda x: x.get('published', datetime.min), reverse=True):
            article_text = (
                f"Title: {article['title']}\n"
                f"Source: {article['source_url']}\n"
                f"Content: {article['content']}\n"
                f"Published: {article.get('published', 'Unknown')}\n"
                "---"
            )
            
            if total_length + len(article_text) > max_length:
                break
                
            context_parts.append(article_text)
            total_length += len(article_text)
        
        return "\n".join(context_parts)

    def _prepare_prompt(
        self,
        context: str,
        prompt: str,
        template: str
    ) -> str:
        """Prepare the full prompt for the LLM"""
        return template.format(
            context=context,
            prompt=prompt,
            current_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        )

    async def _generate_with_openai(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are a professional news writer and analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens or self.config.parameters.get("max_tokens", 2000),
            temperature=self.config.parameters.get("temperature", 0.7),
            presence_penalty=self.config.parameters.get("presence_penalty", 0.0),
            frequency_penalty=self.config.parameters.get("frequency_penalty", 0.0),
        )

        content = response.choices[0].message.content
        return self._parse_llm_response(content, {
            "model": self.config.model_name,
            "tokens": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "provider": "openai"
        })

    async def _generate_with_anthropic(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using Anthropic"""
        try:
            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=max_tokens or self.config.parameters.get("max_tokens", 2000),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.parameters.get("temperature", 0.7)
            )

            # Extract content from the response
            content = response.content[0].text
            
            return self._parse_llm_response(content, {
                "model": self.config.model_name,
                "provider": "anthropic",
                "stop_reason": response.stop_reason,
                "system_fingerprint": response.system_fingerprint
            })
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Anthropic API error: {str(e)}"
            )

    async def _generate_with_custom(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using custom endpoint"""
        try:
            response = await self.client.post(
                "/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens or self.config.parameters.get("max_tokens", 2000),
                    **self.config.parameters
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Custom LLM provider error: {response.text}"
                )

            result = response.json()
            return self._parse_llm_response(result["content"], {
                "model": self.config.model_name,
                "provider": "custom",
                **result.get("metadata", {})
            })
            
        except Exception as e:
            logger.error(f"Custom LLM API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Custom LLM API error: {str(e)}"
            )

    def _parse_llm_response(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        try:
            # Split content into sections using the separator
            sections = content.split("===")
            
            if len(sections) < 4:
                logger.warning("Invalid response format from LLM, attempting to parse content")
                # Fallback parsing logic for malformed responses
                return self._fallback_parse_response(content, metadata)

            # Extract sections
            title = sections[0].strip()
            main_content = sections[1].strip()
            summary = sections[2].strip()
            image_prompt = sections[3].strip()

            # Validate sections
            if not title or not main_content:
                raise ValueError("Missing required content sections")

            return {
                "title": title,
                "content": main_content,
                "summary": summary if summary else main_content[:200] + "...",
                "image_prompt": image_prompt,
                "metadata": {
                    **metadata,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sections_found": len(sections)
                }
            }

        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    def _fallback_parse_response(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback parsing for malformed responses"""
        # Try to extract title from first line
        lines = content.split('\n')
        title = lines[0].strip()
        
        # Use rest as content
        main_content = '\n'.join(lines[1:]).strip()
        
        # Generate a basic summary
        summary = main_content[:200] + "..."
        
        # Create a basic image prompt from title
        image_prompt = f"Create a news-style image representing: {title}"
        
        return {
            "title": title,
            "content": main_content,
            "summary": summary,
            "image_prompt": image_prompt,
            "metadata": {
                **metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "fallback_parsing": True
            }
        }

    def _truncate_context(self, context: str) -> str:
        """Truncate context to fit within token limits"""
        max_length = self.config.parameters.get("max_context_length", 3000)
        if len(context) <= max_length:
            return context
            
        # Split into articles and reconstruct until we hit the limit
        articles = context.split("---")
        truncated_articles = []
        current_length = 0
        
        for article in articles:
            if current_length + len(article) + 3 > max_length:  # +3 for "---"
                break
            truncated_articles.append(article.strip())
            current_length += len(article) + 3
            
        return "---".join(truncated_articles)

    async def validate_api_key(self) -> bool:
        """Validate the API key with the provider"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                # Test with a minimal completion request
                await self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
            elif self.config.provider == LLMProvider.ANTHROPIC:
                await self.client.messages.create(
                    model=self.config.model_name,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Test"}]
                )
            elif self.config.provider == LLMProvider.CUSTOM:
                response = await self.client.get("/health")
                if response.status_code != 200:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.config.provider == LLMProvider.CUSTOM:
            await self.client.aclose()