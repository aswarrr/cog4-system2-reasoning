import json
import os

from google import genai
from google.genai import types

from .base import BaseAIClient
from .prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_user_prompt
from .schemas import ExtractionResult


class GeminiClient(BaseAIClient):
    def __init__(
        self,
        model: str = "gemini-3.1-flash-lite-preview",
        api_key: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY in your environment or pass api_key explicitly."
            )

        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def extract_atomic_facts(self, text: str) -> ExtractionResult:
        user_prompt = build_extraction_user_prompt(text)

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=EXTRACTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
                response_schema=ExtractionResult,
            ),
        )

        # In structured output mode, response.text should contain JSON.
        raw_text = response.text
        if not raw_text:
            raise ValueError("Gemini returned an empty response.")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned non-JSON output: {raw_text}") from exc

        return ExtractionResult.model_validate(parsed)