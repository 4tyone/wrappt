from pydantic import BaseModel
from typing import Type
from wrappt.base import Layer


class Tool(Layer):
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]