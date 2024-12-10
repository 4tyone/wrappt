from pydantic import BaseModel
from typing import Union, TypeVar, Any, Type
from wrappt.base import Layer
from collections.abc import Iterable
from instructor.dsl.partial import Partial

T = TypeVar("T", bound=Union[BaseModel, "Iterable[Any]", "Partial[Any]"])

class Tool(Layer):
    input_schema: Type[BaseModel] #type[T]