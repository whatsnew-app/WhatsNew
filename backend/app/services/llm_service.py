from typing import Dict, List, Optional, Any
import openai
import anthropic
import httpx
from fastapi import HTTPException
from app.models.ai_config import LLMConfig, LLMProvider
from app.schemas.ai_config import LLMConfig as LLMConfigSchema
from datetime import datetime

class LLMService:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._setup_client()

    def _setup_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.config.provider == LLMProvider.OPENAI:
            self.client = openai.Client(api_key=self.config.api_key)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
        elif self.config.provider == LLMProvider.CUSTOM:
            self.client = httpx.AsyncClient(
                base_url=self.config.endpoint_url,
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )

    async def generate_content(
        self,
        articles: List[Dict],
        prompt: str,
        template: str
    ) -> Dict[str, Any]:
        """Generate content using the configured LLM"""
        try:
            # Prepare input for the LLM
            context = self._prepare_context(articles)
            full_prompt = self._prepare_prompt(context, prompt, template)

            # Generate content using appropriate provider
            if self.config.provider == LLMProvider.OPENAI:
                return await self._generate_with_openai(full_prompt)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return await self._generate_with_anthropic(full_prompt)
            elif self.config.provider == LLMProvider.CUSTOM:
                return await self._generate_with_custom(full_prompt)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating content: {str(e)}"
            )

    def _prepare_context(self, articles: List[Dict]) -> str:
        """Prepare context from articles for the LLM"""
        context_parts = []
        for article in articles:
            context_parts.append(
                f"Title: {article['title']}\n"
                f"Source: {article['source_url']}\n"
                f"Content: {article['content']}\n"
                f"Published: {article['published']}\n"
                "---"
            )
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
            current_date=datetime.utcnow().strftime("%Y-%m-%d")
        )

    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are a professional news writer."},
                {"role": "user", "content": prompt}
            ],
            **self.config.parameters
        )

        # Parse the response
        content = response.choices[0].message.content
        return self._parse_llm_response(content, {
            "model": self.config.model_name,
            "tokens": response.usage.total_tokens,
            "provider": "openai"
        })

    async def _generate_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Anthropic"""
        response = await self.client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.parameters.get("max_tokens", 1000),
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_llm_response(response.content[0].text, {
            "model": self.config.model_name,
            "provider": "anthropic"
        })

    async def _generate_with_custom(self, prompt: str) -> Dict[str, Any]:
        """Generate content using custom endpoint"""
        response = await self.client.post(
            "/generate",
            json={
                "prompt": prompt,
                **self.config.parameters
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error from custom LLM provider"
            )

        result = response.json()
        return self._parse_llm_response(result["content"], {
            "model": self.config.model_name,
            "provider": "custom"
        })

    def _parse_llm_response(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        # Split content into sections
        sections = content.split("===")
        
        if len(sections) < 4:
            raise ValueError("Invalid response format from LLM")

        return {
            "title": sections[0].strip(),
            "content": sections[1].strip(),
            "summary": sections[2].strip(),
            "image_prompt": sections[3].strip(),
            "metadata": metadata
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.config.provider == LLMProvider.CUSTOM:
            await self.client.aclose()