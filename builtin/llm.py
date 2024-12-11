from pydantic import BaseModel
from typing import Optional, List, Dict, Type
import instructor
from anthropic import Anthropic
import openai
from wrappt.base import Layer, Pill


class LLMInputSchema(BaseModel):
    query: str

class LLMOutputSchema(BaseModel):
    response: str


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
            
    def set_input_schema(self, new_schema: Type[BaseModel]):
        """Sets a new input schema dynamically."""
        if not issubclass(new_schema, BaseModel):
            raise TypeError("Input schema must be a subclass of BaseModel.")
        self.input_schema = new_schema

    def set_output_schema(self, new_schema: Type[BaseModel]):
        """Sets a new output schema dynamically."""
        if not issubclass(new_schema, BaseModel):
            raise TypeError("Output schema must be a subclass of BaseModel.")
        self.output_schema = new_schema
        
    def run(self, input: Pill, chat_history: Optional[List[Dict]] = None) -> Pill:
        # TODO: implement error handling with Pill
        self.pill_validator(pill=input)
        
        messages = [
            {
                "role": "system",
                "content": str(input.data),
            }
        ]

        if chat_history:
            messages.extend(chat_history)

        new_message = {
            "role": "user",
            "content": input.data.query,
        }

        messages.append(new_message)

        response = self._get_client().chat.completions.create(
            messages=messages,
            model=self.model,
            response_model=self.output_schema,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return Pill(handler=input.handler, data=response)