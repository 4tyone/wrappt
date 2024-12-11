from wrappt.base import Handler, Pill
from wrappt.builtin.tool import Tool
from pydantic import BaseModel
from typing import Type

def sequential_builder():
    # TODO: implement
    pass

def handle_err_builder(handler: Handler):
    # TODO: analyzes the handler you give to it and finds every usage and every kind of error inputed into handle_err 
    # and builds a match-case based handler for every kind of error object
    # this needs to be a wrappt cli command
    # one idea is to make a decorator for the handle_err of a specific Handler object that will mark it so that the CLI tool will know which handler to build
    pass


class ChosenToolSchema(BaseModel):
            chosen_tool: str

class ToolPickerTool(Tool):
    output_schema: Type[BaseModel] = ChosenToolSchema

    def run(self, input: Pill) -> Pill:
        attributes = input.data.model_dump()

        if not all(isinstance(value, bool) for value in attributes.values()):
            return input.handler.handle_err(ValueError("All attributes must be boolean."))

        true_attributes = [key for key, value in attributes.items() if value]

        if len(true_attributes) == 0:
            return input.handler.handle_err(ValueError("At least one attribute must be True."))
        elif len(true_attributes) > 1:
            return input.handler.handle_err(ValueError("Only one attribute must be True."))

        chosen_tool = input.handler.handle_ok(true_attributes[0])
        return Pill(handler=input.handler, data=self.output_schema(chosen_tool=chosen_tool))