from pydantic import BaseModel
from typing import Optional, List, Dict, Type
import instructor
from anthropic import Anthropic
import openai
import google.generativeai as genai


class LLMInputSchema(BaseModel):
    query: str

class LLMOutputSchema(BaseModel):
    response: str


class LLM(BaseModel):
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
            case "deepseek":
                return instructor.from_openai(
                                                openai.OpenAI(
                                                    base_url="https://api.deepseek.com",
                                                    api_key=self.api_key,
                                                ),
                                                mode=instructor.Mode.JSON,
                                                )
            case "google":
                genai.configure(api_key=self.api_key)
                return instructor.from_gemini(
                                                client=genai.GenerativeModel(
                                                            model_name=self.model,
                                                        ),
                                                mode=instructor.Mode.GEMINI_JSON,
                                                )
            case _:
                raise NotImplementedError(f"The provider {self.provider} is not implemented yet.")
        
    def generate(self, messages: List[Dict], output_schema: Type[BaseModel]) -> BaseModel:
    
        if self.provider == "google":

            config = {
                        "response_mime_type": "application/json"#, response_schema=list[SiReOutputSchema]
            }
            response = self._get_client().chat.completions.create(
                messages=messages,
                response_model=output_schema,
                generation_config=config
            )
        else:
            response = self._get_client().chat.completions.create(
                messages=messages,
                model=self.model,
                response_model=output_schema,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

        return response