"""LLM integration for code analysis."""

import json
from typing import Any, Dict, List, Optional

import httpx
import ollama
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMEngine:
    """LLM engine for code analysis."""

    def __init__(self) -> None:
        """Initialize LLM engine."""
        self.ollama_client = None
        self.openai_client = None

        # Initialize Ollama
        try:
            self.ollama_client = ollama.Client(host=settings.ollama_base_url)
            logger.info("Ollama client initialized", url=settings.ollama_base_url)
        except Exception as e:
            logger.warning("Failed to initialize Ollama", error=str(e))

        # Initialize OpenAI if API key is provided
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")

    async def analyze_code(
        self,
        code: str,
        language: str,
        file_path: str,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze code for vulnerabilities, review, and auto-comment.

        Args:
            code: Code content to analyze
            language: Programming language
            file_path: File path
            context: Optional RAG context chunks

        Returns:
            Analysis results dictionary
        """
        prompt = self._build_analysis_prompt(code, language, file_path, context)

        try:
            # Try Ollama first
            if self.ollama_client:
                result = await self._analyze_with_ollama(prompt)
                if result:
                    return result
        except Exception as e:
            logger.warning("Ollama analysis failed", error=str(e))

        # Fallback to OpenAI
        if self.openai_client and settings.use_openai_fallback:
            try:
                return await self._analyze_with_openai(prompt)
            except Exception as e:
                logger.error("OpenAI analysis failed", error=str(e))

        # Return empty result if all fail
        logger.error("All LLM providers failed")
        return {
            "vulnerabilities": [],
            "code_review": [],
            "auto_comments": [],
        }

    def _build_analysis_prompt(
        self,
        code: str,
        language: str,
        file_path: str,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build analysis prompt for LLM."""
        context_text = ""
        if context:
            context_text = "\n\n## Related Code Context:\n"
            for ctx in context[:3]:  # Use top 3 context chunks
                context_text += f"\n### {ctx.get('file_path', 'unknown')} (lines {ctx.get('start_line', 0)}-{ctx.get('end_line', 0)}):\n```{ctx.get('language', '')}\n{ctx.get('content', '')}\n```\n"

        prompt = f"""You are an expert security engineer and code reviewer. Analyze the following {language} code for:

1. **Vulnerabilities**: Detect OWASP Top 10, CWE patterns, insecure functions, hardcoded secrets, weak crypto, SQL injection, XSS, RCE, etc.
2. **Code Review**: Suggest improvements for performance, readability, idioms, refactoring, design patterns.
3. **Auto-Comments**: Add inline comments explaining complex logic, edge cases, or missing documentation.

{context_text}

## Code to Analyze:

File: {file_path}
Language: {language}

```{language}
{code}
```

## Output Format (JSON):

{{
  "vulnerabilities": [
    {{
      "severity": "critical|high|medium|low",
      "title": "Vulnerability title",
      "description": "Detailed description",
      "start_line": 10,
      "end_line": 15,
      "cwe_id": "CWE-79",
      "owasp_category": "A03:2021 – Injection",
      "suggestion": "How to fix",
      "code_snippet": "vulnerable code",
      "fixed_code": "fixed code"
    }}
  ],
  "code_review": [
    {{
      "severity": "info|low|medium",
      "title": "Review finding title",
      "description": "Description",
      "start_line": 20,
      "end_line": 25,
      "suggestion": "Improvement suggestion",
      "code_snippet": "current code",
      "fixed_code": "improved code"
    }}
  ],
  "auto_comments": [
    {{
      "line": 30,
      "comment": "Explanation of complex logic"
    }}
  ]
}}

Return ONLY valid JSON, no markdown formatting or additional text."""

        return prompt

    async def _analyze_with_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Analyze code using Ollama."""
        try:
            response = self.ollama_client.generate(
                model=settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "num_predict": 4000,
                },
            )

            result_text = response.get("response", "")
            # Extract JSON from response
            json_text = self._extract_json(result_text)
            return json.loads(json_text)
        except Exception as e:
            logger.error("Ollama analysis error", error=str(e))
            # Try fallback model
            if settings.ollama_fallback_model != settings.ollama_model:
                try:
                    response = self.ollama_client.generate(
                        model=settings.ollama_fallback_model,
                        prompt=prompt,
                        options={"temperature": 0.1, "num_predict": 4000},
                    )
                    result_text = response.get("response", "")
                    json_text = self._extract_json(result_text)
                    return json.loads(json_text)
                except Exception as e2:
                    logger.error("Ollama fallback model error", error=str(e2))
            return None

    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze code using OpenAI."""
        response = await self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert security engineer and code reviewer. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=4000,
        )

        result_text = response.choices[0].message.content or "{}"
        json_text = self._extract_json(result_text)
        return json.loads(json_text)

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text response."""
        # Try to find JSON in code blocks
        import re

        json_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # Try to find JSON object directly
        json_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return text.strip()

