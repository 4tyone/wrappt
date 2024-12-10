from wrappt.base import Pipeline, Pill
from wrappt.builtin.llm import LLM
from wrappt.builtin.tool import Tool
from wrappt.builtin.prompts import tool_picker_prompt
from pydantic import create_model
from typing import List, Dict


class Sequential(Pipeline): #TODO: This will not work, needs to be fixed
    def forward(self, input: Pill) -> Pill:
        x = input
        for layer in self.layers:
            x = layer.run(x)

        return x

  
class JobWorker(Pipeline):
    def __init__(self, layers):
        super().__init__(layers=layers)
        self.tools: Dict[str, str] = {}
        self.tool_objects: Dict[str, Tool] = {}
        self.llm = None

        for layer in self.layers:
            if isinstance(layer, Tool):
                self.tools[layer.name] = layer.context
                self.tool_objects[layer.name] = layer
            elif isinstance(layer, LLM):
                self.llm = layer

        if not self.llm:
            raise Exception("LLM object is missing")

        tool_picker_prompt.patch(
            tool_names_and_descriptions="\n    " + "\n".join(f"{key}: {value}" for key, value in self.tools.items())
        )
        self.ToolPickerPrompt = tool_picker_prompt.get_prompt()

        class ToolPickerTool(Tool):
            def run(self, input: Pill) -> Pill:
                attributes = input.input_obj.model_dump()  # Convert to dict if needed

                if not all(isinstance(value, bool) for value in attributes.values()):
                    return input.handler.handle_err(ValueError("All attributes must be boolean."))

                true_attributes = [key for key, value in attributes.items() if value]

                if len(true_attributes) == 0:
                    return input.handler.handle_err(ValueError("At least one attribute must be True."))
                elif len(true_attributes) > 1:
                    return input.handler.handle_err(ValueError("Only one attribute must be True."))

                chosen_tool = input.handler.handle_ok(true_attributes[0])
                # Return a Pill with the chosen tool name stored in a known attribute
                return Pill(handler=input.handler, chosen_tool=chosen_tool)
            
        self.ToolPickerSchema = self._tool_picker_schema("ToolPickerSchema", list(self.tools.keys()))

        self.tool_picker_tool = ToolPickerTool(
            name="tool_picker_tool",
            context="This tool returns the correct tool that the LLM chooses",
            input_schema=self.ToolPickerSchema
        )

    def _tool_picker_schema(self, name: str, tool_names: List[str]):
        """
        Create a Pydantic model where each field is a boolean.
        The LLM will decide which tool is True.
        """
        fields = {field_name: (bool, ...) for field_name in tool_names}
        Base = create_model(name, **fields)
        return Base

    def forward(self, input: Pill) -> Pill:
        tool_picker_pill = Pill(handler=input.handler, query=input.query, prompt=self.ToolPickerPrompt)
        response = self.llm.run(input=tool_picker_pill, output_schema=self.ToolPickerSchema)
        print(response)
        response = Pill(handler=input.handler,
                        input_obj=response)

        picked_tool = self.tool_picker_tool.run(response)
        tool_name = picked_tool.chosen_tool
        tool_object = self.tool_objects[tool_name]
        response = self.llm.run(input=input, output_schema=tool_object.input_schema)
        print(response)
        result = tool_object.run(input=response)

        return result
        