from pydantic import BaseModel, ValidationError, ConfigDict
from typing import Dict, Tuple, Any, List, Dict, Union
from functools import wraps


class ErrorInputModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    error: Exception


class Handler:
    @staticmethod
    def validate_handle_err(func):
        """Decorator to validate the 'error' parameter."""
        @wraps(func)
        def wrapper(self, error, *args, **kwargs):
            try:
                ErrorInputModel(error=error)
            except ValidationError as e:
                raise ValueError(f"Invalid input for handle_err: {e}")
            return func(self, error, *args, **kwargs)
        return wrapper

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'handle_err' in cls.__dict__:
            original_method = cls.__dict__['handle_err']
            cls.handle_err = Handler.validate_handle_err(original_method)
        else:
            raise TypeError("Subclass must override the handle_err method")
        if 'handle_ok' not in cls.__dict__:
            raise TypeError("Subclass must override the handle_ok method")

    def handle_ok(self, *args: Any, **kwargs: Dict[str, Any]):
        raise NotImplementedError("The handle_ok method should be implemented by subclasses.")

    def handle_err(self, error: Exception):
        raise NotImplementedError("The handle_err method should be implemented by subclasses.")


class Pill(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    handler: Handler


class Layer(BaseModel):
    name: str
    context: str

    def run(self, input: Pill) -> Any:
        raise NotImplementedError("The run method should be implemented by subclasses.")

    def get_context(self) -> str:
        return self.context


class Pipeline(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    layers: List[Layer] = []
    input_schema: BaseModel = None
    output_schema: BaseModel = None
    
    def __init__(self, layers):
        super().__init__(layers=layers)

    def forward(self, input: Pill) -> Any:
        raise NotImplementedError("The forward method should be implemented by subclasses.")


class Prompt(BaseModel):
    prompt_schema: Dict[str, Union[str, None]]

    def get_prompt(self) -> str:
        return "\n".join(f"{key}: {value}" for key, value in self.prompt_schema.items())

    def patch(self, **kwargs: Dict[str, str]):
        for key, value in kwargs.items():
            if key in self.prompt_schema:
                self.prompt_schema[key] = value
            else:
                raise KeyError(f"Component '{key}' does not exist in prompt_schema.")



if __name__ == "__main__":
    # handler = Handler()
    # pill = Pill(handler, 4)

    # tool = Tool(context="sup", tool_name="suup", api_schema=pill)


    # prompt = Prompt(prompt_schema={
    #         "sup": "heyaaa"
    #     })

    # print(prompt.get_prompt())

    class MyHandler(Handler):
        def handle_err(self, error: Exception):
            print(f"Handling error: {error}")
        def handle_ok(self, error):
            print(f"Handling error: {error}")

    # Example
    handler = MyHandler()
    handler.handle_err(ValueError("This is a valid error"))  # Works fine


    # class MyHandler(Handler):
    #     def handle_err(self, error):
    #         print(f"Handling error: {error}")

    # handler = MyHandler()
    # handler.handle_err("This is not an Exception")  # Invalid input

    # class MyHandler(Handler):
    #     pass

