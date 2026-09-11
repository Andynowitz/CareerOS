from __future__ import annotations

import os
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class AIClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set."
            )

        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        response = await self.client.responses.parse(
            model="gpt-5.6-luna",
            input=prompt,
            text_format=response_model,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "OpenAI returned no structured response."
            )

        return response.output_parsed