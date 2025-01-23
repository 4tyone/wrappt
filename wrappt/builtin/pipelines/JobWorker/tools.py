from wrappt.base import Pill, Layer
from wrappt.builtin.llm import LLM
from typing import List
from pydantic import BaseModel


class ChosenToolSchema(BaseModel):
    chosen_tool: str

class ToolPickerTool(Layer):
    llm: LLM

    def run(self, input: Pill, tool_names: List[str]) -> Pill:
        self.pill_validator(pill=input)

        response = self.llm.generate(input=input, output_schema=self.output_schema)
        chosen_tool = response.chosen_tool

        if chosen_tool not in tool_names:
            return input.handler.handle_err(ValueError(f"Invalid tool name: {chosen_tool}"))

        return Pill(
            handler=input.handler,
            data=self.output_schema(chosen_tool=input.handler.handle_ok(chosen_tool))
        )