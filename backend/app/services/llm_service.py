# app/services/llm_service.py

from typing import Dict, List, Optional, Any
import openai
from openai import AsyncOpenAI
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
        logger.info(f"Initializing LLM service with config id: {config.id}")
        self.config = config
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """Initialize the appropriate LLM client based on provider"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self.client = AsyncOpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.endpoint_url
                )
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

    def _prepare_articles_context(self, articles: List[Dict]) -> str:
        """Prepare articles context for LLM prompt."""
        context_parts = []
        max_length = self.config.parameters.get("max_context_length", 3000)
        current_length = 0

        for article in sorted(articles, key=lambda x: x.get('published', ''), reverse=True):
            article_text = self._format_article_text(article)
            
            # Check if adding this article would exceed max length
            if current_length + len(article_text) > max_length:
                break
                
            context_parts.append(article_text)
            current_length += len(article_text)
        
        return "\n\n".join(context_parts)

    def _format_article_text(self, article: Dict[str, Any]) -> str:
        """Format a single article for context."""
        return (
            f"Title: {article.get('title', '')}\n"
            f"Source: {article.get('link', article.get('source_url', ''))}\n"
            f"Date: {article.get('published', '')}\n"
            f"Content: {article.get('content', '')}\n"
            "---"
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
            articles_context = self._prepare_articles_context(articles)
            logger.info(f"Prepared context from {len(articles)} articles")
            
            # Create system message with strict formatting instructions
            system_message = (
                "You are an expert journalist and news analyst. Your response MUST follow this exact format:\n\n"
                "=== Title ===\n"
                "<Write the headline here>\n\n"
                "=== Content ===\n"
                "<Write the main content here>\n\n"
                "=== Summary ===\n"
                "<Write a one-paragraph summary here>\n\n"
                "=== Image Prompt ===\n"
                "<Write the image generation prompt here>\n\n"
                "Rules:\n"
                "1. Include ALL four sections with exact headers as shown above\n"
                "2. Each section must be non-empty\n"
                "3. The Title must be clear and engaging\n"
                "4. The Content must use bullet points for clarity\n"
                "5. The Summary must be exactly one paragraph\n"
                "6. The Image Prompt must describe a specific image"
            )
            
            # Format the full prompt using template
            full_prompt = template.format(
                context=articles_context,
                prompt=prompt,
                current_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            )

            logger.info("Formatting complete. Beginning content generation.")

            # Generate content using appropriate provider
            start_time = datetime.utcnow()
            
            if self.config.provider == LLMProvider.OPENAI:
                result = await self._generate_with_openai(
                    system_message,
                    full_prompt,
                    max_tokens
                )
            elif self.config.provider == LLMProvider.ANTHROPIC:
                result = await self._generate_with_anthropic(
                    system_message,
                    full_prompt,
                    max_tokens
                )
            elif self.config.provider == LLMProvider.CUSTOM:
                result = await self._generate_with_custom(
                    system_message,
                    full_prompt,
                    max_tokens
                )
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Content generation completed in {generation_time:.2f} seconds")
            
            # Add performance metrics
            if isinstance(result, dict) and "metadata" in result:
                result["metadata"]["generation_time"] = generation_time
                result["metadata"]["prompt_length"] = len(full_prompt)
                result["metadata"]["article_count"] = len(articles)
            
            return result

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {str(e)}"
            )

    async def _generate_with_openai(
        self,
        system_message: str,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using OpenAI with enhanced logging"""
        try:
            logger.info("Sending request to OpenAI with:")
            logger.info(f"System message: {system_message}")
            logger.info(f"Prompt preview: {prompt[:200]}...")
            
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.config.parameters.get("max_tokens", 2000),
                temperature=self.config.parameters.get("temperature", 0.7),
                presence_penalty=self.config.parameters.get("presence_penalty", 0.0),
                frequency_penalty=self.config.parameters.get("frequency_penalty", 0.0),
            )

            content = response.choices[0].message.content
            logger.info("Received response from OpenAI:")
            logger.info(f"Raw response: {content}")
            
            # Check for section markers before parsing
            if "=== Title ===" not in content:
                logger.error("Response is missing Title section marker")
            if "=== Content ===" not in content:
                logger.error("Response is missing Content section marker")
            if "=== Summary ===" not in content:
                logger.error("Response is missing Summary section marker")
            if "=== Image Prompt ===" not in content:
                logger.error("Response is missing Image Prompt section marker")

            return self._parse_llm_response(content, {
                "model": self.config.model_name,
                "tokens": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "provider": "openai"
            })
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(e)}"
            )

    async def _generate_with_anthropic(
        self,
        system_message: str,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using Anthropic"""
        try:
            logger.info("Sending request to Anthropic")
            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=max_tokens or self.config.parameters.get("max_tokens", 2000),
                messages=[
                    {
                        "role": "user",
                        "content": f"{system_message}\n\n{prompt}"
                    }
                ],
                temperature=self.config.parameters.get("temperature", 0.7)
            )

            # Extract content from the response
            content = response.content[0].text
            logger.info(f"Received response from Anthropic: {content[:200]}...")
            
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
        system_message: str,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate content using custom endpoint"""
        try:
            logger.info("Sending request to custom endpoint")
            response = await self.client.post(
                "/generate",
                json={
                    "system_message": system_message,
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
            logger.info(f"Received response from custom endpoint: {result.get('content', '')[:200]}...")
            
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
        """Parse LLM response with enhanced error reporting"""
        try:
            # Log the exact content being parsed
            logger.info("Starting to parse content:")
            logger.info(f"Content length: {len(content)}")
            logger.info(f"Content preview: {content[:200]}...")
            
            # First check if all required sections exist
            required_sections = [
                "=== Title ===",
                "=== Content ===",
                "=== Summary ===",
                "=== Image Prompt ==="
            ]
            
            missing_sections = [
                section for section in required_sections 
                if section not in content
            ]
            
            if missing_sections:
                error_msg = f"Missing sections: {', '.join(missing_sections)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Split content into sections using regex
            import re
            sections = re.split(r'===\s*([^=]+?)\s*===', content)
            
            # Remove empty strings and organize sections
            sections = [s.strip() for s in sections if s.strip()]
            section_dict = {}
            
            # Log the sections found
            logger.info(f"Found {len(sections)} sections after splitting")
            
            # Pair section headers with their content
            for i in range(0, len(sections)-1, 2):
                section_name = sections[i].lower()
                section_content = sections[i+1]
                section_dict[section_name] = section_content
                logger.info(f"Parsed section: {section_name}")
                logger.info(f"Content preview: {section_content[:50]}...")

            # Construct the response
            result = {
                "title": section_dict.get('title', ''),
                "content": section_dict.get('content', ''),
                "summary": section_dict.get('summary', ''),
                "image_prompt": section_dict.get('image prompt', ''),
                "metadata": {
                    **metadata,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sections_found": len(section_dict)
                }
            }

            # Validate the result
            if not all(result.values()):
                missing = [k for k, v in result.items() if not v and k != 'metadata']
                error_msg = f"Missing content for sections: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return result

        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.error(f"Raw content causing error: {content}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    def _fallback_parse_response(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback parsing for malformed responses"""
        logger.info("Attempting fallback parsing for malformed response")
        # Try to extract title from first line
        lines = content.split('\n')
        title = lines[0].strip()
        
        # Use rest as content
        main_content = '\n'.join(lines[1:]).strip()
        
        # Generate a basic summary
        summary = main_content[:200] + "..."
        
        # Create a basic image prompt from title
        image_prompt = f"Create a news-style image representing: {title}"
        
        logger.info("Fallback parsing completed")
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
            """Async context manager entry"""
            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
            """Async context manager exit"""
            if self.config.provider == LLMProvider.CUSTOM:
                await self.client.aclose()