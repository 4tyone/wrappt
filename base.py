from pydantic import BaseModel
from typing import Dict, Tuple, Any, Union


class Handler(BaseModel):
    def handle_ok(self, *args: Any, **kwargs: Dict[str, Any]):
        raise NotImplementedError("The handle_ok method should be implemented by subclasses.")

    def handle_err(self, *args: Any, **kwargs: Dict[str, Any]):
        raise NotImplementedError("The handle_err method should be implemented by subclasses.")


class Pill(BaseModel):
    handler: Handler
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}

    class Config:
        extra = 'allow'

    def __init__(self, handler: Handler, *args: Any, **kwargs: Dict[str, Any]):
        super().__init__(handler=handler, args=args, kwargs=kwargs)


class Layer(BaseModel):
    context: str

    def run(self, input: Union[str, Pill], *args: Union[Any, Pill], **kwargs: Dict[str, Union[Any, Pill]]) -> str:
        raise NotImplementedError("The run method should be implemented by subclasses.")

    def get_context(self) -> str:
        return self.context


class Pipeline(BaseModel):
    layers: Dict[str, Layer]= {}

    class Config:
        extra = 'allow'

    def __init__(self, **layers):
        super().__init__(layers=layers)

    def forward(self, input: Union[str, Pill], *args: Union[Any, Pill], **kwargs: Dict[str, Union[Any, Pill]]) -> str:
        raise NotImplementedError("The forward method should be implemented by subclasses.")


class Prompt(BaseModel):
    prompt_schema: Dict[str, str]

    def get_prompt(self) -> str:
        return "\n".join(self.prompt_schema.values())

    def patch(self, **kwargs: Dict[str, Union[str, Pill]]):
        for key, value in kwargs.items():
            if key in self.prompt_schema:
                self.prompt_schema[key] = value
            else:
                raise KeyError(f"Component '{key}' does not exist in prompt_schema.")


class Tool(Layer):
    tool_name: str
    api_schema: BaseModel


class LLM(Layer):
    llm: Any


if __name__ == "__main__":
    handler = Handler()
    pill = Pill(handler, 4)

    tool = Tool(context="sup", tool_name="suup", api_schema=pill)


    prompt = Prompt(prompt_schema={
            "sup": "heyaaa"
        })

    print(prompt.get_prompt())
