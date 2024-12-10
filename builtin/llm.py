from pydantic import BaseModel
from typing import Optional, List, Dict
import instructor
from anthropic import Anthropic
import openai
from wrappt.base import Layer, Pill

class OutputSchema(BaseModel):
    output: str

class LLM(Layer):
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
            case _:
                raise NotImplementedError(f"The provider {self.provider} is not implemented yet.")
        

    def run(self, input: Pill, chat_history: Optional[List[Dict]] = None, output_schema: BaseModel = OutputSchema) -> BaseModel:
        # TODO: implement error handling with Pill
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
            "content": input.query,
        }

        messages.append(new_message)

        response = self._get_client().chat.completions.create(
            messages=messages,
            model=self.model,
            response_model=output_schema,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response