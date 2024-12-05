from pydantic import BaseModel
from typing import Dict, Tuple, Any, Union

class Handler(BaseModel):
    def handle_ok(self, *args, **kwargs):
        raise NotImplementedError("The handle_ok method should be implemented by subclasses.")

    def handle_err(self, *args, **kwargs):
        raise NotImplementedError("The handle_err method should be implemented by subclasses.")

class Pill(BaseModel):
    handler: Handler
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}

    class Config:
        extra = 'allow'

    def __init__(self, *args, handler: Handler, **kwargs):
        super().__init__(handler=handler)
        self.args = args
        self.kwargs = kwargs

class Layer(BaseModel):
    context: str

    def run(self, input: Union[str, Pill], *args, **kwargs) -> str:
        raise NotImplementedError("The run method should be implemented by subclasses.")

    def get_context(self) -> str:
        return self.context

class Pipeline(BaseModel):
    blocks: Dict[str, Layer]

    def forward(self, input: Union[str, Pill], *args, **kwargs) -> str:
        raise NotImplementedError("The forward method should be implemented by subclasses.")

class Prompt(BaseModel):
    prompt_schema: Dict[str, str]

    def get_prompt(self) -> str:
        return "\n".join(self.prompt_schema.values())

    def patch(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.prompt_schema:
                self.prompt_schema[key] = value
            else:
                raise KeyError(f"Component '{key}' does not exist in prompt_schema.")

class Tool(Layer):
    def run(self, input: Union[str, Pill], *args, **kwargs) -> str:
        raise NotImplementedError("The run method should be implemented by subclasses.")

class LLM(Layer):
    llm: Any # TODO: create a LLM object that goes here

    def run(self, input:  Union[str, Pill], *args, **kwargs) -> str:
        raise NotImplementedError("The run method should be implemented by subclasses.")
    
handler = Handler()
pill = Pill(handler=handler)
