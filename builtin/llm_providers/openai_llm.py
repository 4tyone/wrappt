import instructor
import openai
from wrappt.builtin.llm_providers.base_llm import BaseLLM


class OpenAILLM(BaseLLM):
    def __init__(self, api_key, *args, **kwargs):
        self.api_key = api_key
        super().__init__(*args, **kwargs)

    def _get_client(self):
        return instructor.from_openai(openai.OpenAI(api_key=self.api_key))


if __name__ == "__main__":
    from pydantic import BaseModel

    class OutputSchema(BaseModel):
        output: str


    llm = OpenAILLM(model="gpt-4o-mini",
                    api_key="",
                    system_prompt="You are a helpful assistant",
                    output_schema=OutputSchema,
                    temperature=1)

    print(llm.generate(role="user", query="Hello").output)