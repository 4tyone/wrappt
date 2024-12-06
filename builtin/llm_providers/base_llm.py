from pydantic import BaseModel
from typing import Optional, List, Dict

class BaseLLM:
    def __init__(self, model: str, system_prompt: str, output_schema: BaseModel, temperature: int, max_tokens: Optional[int] = 8192):
        self.model = model
        self.client = self._get_client()
        self.system_prompt = system_prompt
        self.output_schema = output_schema
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def _get_client(self):
        raise NotImplementedError("This needs to be implemented to be able to connect to the client.")

    def generate(self, role: str, query: str, chat_history: Optional[List[Dict]] = None):
        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        if chat_history:
            messages.extend(chat_history)

        new_message = {
            "role": role,
            "content": query,
        }

        messages.append(new_message)

        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            response_model=self.output_schema,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response