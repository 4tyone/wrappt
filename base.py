from pydantic import BaseModel, ValidationError, ConfigDict
from typing import Dict, Any, List, Dict, Optional, Type
from abc import abstractmethod
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

    @abstractmethod
    def handle_ok(self, *args: Any, **kwargs: Dict[str, Any]):
        raise NotImplementedError("The handle_ok method should be implemented by subclasses.")

    @abstractmethod
    def handle_err(self, error: Exception):
        raise NotImplementedError("The handle_err method should be implemented by subclasses.")


class Pill(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    handler: Handler
    data: BaseModel


class Layer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    name: str
    context: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    llm: Optional[BaseModel] = None

    @abstractmethod
    def run(self, input: Pill, *args, **kwargs) -> Pill:
        raise NotImplementedError("The run method should be implemented by subclasses.")

    def get_context(self) -> str:
        return self.context
    
    def pill_validator(self, pill: Pill):
        try:
            _ = self.input_schema.model_validate(pill.data)
        except ValidationError as e:
            raise ValidationError("Validation error:", e)


class Pipeline(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    layers: List[Layer]
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    llm: Optional[BaseModel] = None
    
    def __init__(self, layers, output_schema):
        super().__init__(layers=layers,output_schema=output_schema)

    @abstractmethod
    def forward(self, input: Pill, *args, **kwargs) -> Pill:
        raise NotImplementedError("The forward method should be implemented by subclasses.")



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

