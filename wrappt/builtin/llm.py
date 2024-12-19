from pydantic import BaseModel
from typing import Optional, List, Dict, Type
import instructor
from anthropic import Anthropic
import openai
from wrappt.base import Pill


class LLMInputSchema(BaseModel):
    query: str

class LLMOutputSchema(BaseModel):
    response: str


class LLM(BaseModel):
    context: str
    provider: str
    model: str
    api_key: str
    temperature: Optional[int] = 0
    max_tokens: Optional[int] = 8192
        
    def _get_client(self):
        match self.provider:
            case "anthropic":
                return instructor.from_anthropic(Anthropic(api_key=self.api_key))
            case "openai":
                return instructor.from_openai(openai.OpenAI(api_key=self.api_key))
            case "ollama":
                return instructor.from_openai(
                                                openai.OpenAI(
                                                    base_url="http://localhost:11434/v1",
                                                    api_key="ollama",
                                                ),
                                                mode=instructor.Mode.JSON,
                                                )
            case _:
                raise NotImplementedError(f"The provider {self.provider} is not implemented yet.")
        
    def generate(self, input: Pill, output_schema: Type[BaseModel], chat_history: Optional[List[Dict]] = None) -> Pill:
        # TODO: implement error handling with Pill
        # TODO: implement token/cost counter
        
        messages = [
            {
                "role": "system",
                "content": self.context,
            }
        ]

        if chat_history:
            messages.extend(chat_history)

        new_message = {
            "role": "user",
            "content": str(input.data),
        }

        messages.append(new_message)

        response = self._get_client().chat.completions.create(
            messages=messages,
            model=self.model,
            response_model=output_schema,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return Pill(handler=input.handler, data=response)