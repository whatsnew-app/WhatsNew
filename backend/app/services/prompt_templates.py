from typing import Dict, Optional

class PromptTemplates:
    """Collection of prompt templates for different news styles"""

    @staticmethod
    def get_template(template_type: str) -> str:
        """Get prompt template by type"""
        templates = {
            "summary": """
            Based on the following news articles:
            {context}

            Create a comprehensive news summary following these guidelines:
            1. Write a clear, engaging title
            2. Provide detailed analysis and synthesis of the information
            3. Include key facts and figures
            4. Maintain journalistic objectivity
            5. {prompt}

            Format your response as follows:
            [Title]
            ===
            [Main Content]
            ===
            [Brief Summary]
            ===
            [Image Generation Prompt]
            """,

            "analysis": """
            Analyze the following news articles:
            {context}

            Create an in-depth analysis following these guidelines:
            1. Write an analytical title
            2. Provide context and background
            3. Analyze trends and implications
            4. Include expert perspectives if available
            5. {prompt}

            Format your response as follows:
            [Title]
            ===
            [Analysis Content]
            ===
            [Key Takeaways]
            ===
            [Image Generation Prompt]
            """,

            "narrative": """
            Based on these news articles:
            {context}

            Create an engaging narrative following these guidelines:
            1. Write a compelling headline
            2. Tell a coherent story
            3. Include relevant quotes and details
            4. Maintain factual accuracy
            5. {prompt}

            Format your response as follows:
            [Title]
            ===
            [Narrative Content]
            ===
            [Story Summary]
            ===
            [Image Generation Prompt]
            """,

            "technical": """
            Based on the following technical news:
            {context}

            Create a technical analysis following these guidelines:
            1. Write a technical but accessible title
            2. Explain complex concepts clearly
            3. Include technical details and specifications
            4. Provide practical implications
            5. {prompt}

            Format your response as follows:
            [Title]
            ===
            [Technical Content]
            ===
            [Technical Summary]
            ===
            [Image Generation Prompt]
            """
        }

        return templates.get(template_type, templates["summary"])

    @staticmethod
    def get_metadata() -> Dict[str, Dict[str, str]]:
        """Get metadata about available templates"""
        return {
            "summary": {
                "name": "News Summary",
                "description": "Comprehensive summary of news articles"
            },
            "analysis": {
                "name": "Deep Analysis",
                "description": "In-depth analysis of news and trends"
            },
            "narrative": {
                "name": "Narrative Style",
                "description": "Story-driven news presentation"
            },
            "technical": {
                "name": "Technical Report",
                "description": "Technical analysis and explanation"
            }
        }