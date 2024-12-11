from wrappt.base import Pipeline, Pill
from wrappt.builtin.llm import LLM, LLMInputSchema
from wrappt.builtin.tool import Tool
from wrappt.builtin.utils import ToolPickerTool
from wrappt.builtin.prompts import tool_picker_prompt, job_worker_prompt
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

        self.tool_picker_prompt = tool_picker_prompt
        self.job_worker_prompt = job_worker_prompt

        for layer in self.layers:
            if isinstance(layer, Tool):
                self.tools[layer.name] = layer.context
                self.tool_objects[layer.name] = layer
            elif isinstance(layer, LLM):
                self.llm = layer

        if not self.llm:
            raise Exception("LLM object is missing")

        self.tool_picker_prompt.patch(
            tool_names_and_descriptions="\n    " + "\n".join(f"{key}: {value}" for key, value in self.tools.items())
        )
  
        self.ToolPickerSchema = self._tool_picker_schema("ToolPickerSchema", list(self.tools.keys()))

        self.tool_picker_tool = ToolPickerTool(
            name="tool_picker_tool",
            context="This tool returns the correct tool that the LLM chooses",
            input_schema=self.ToolPickerSchema,
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
        self.tool_picker_prompt.patch(data=str(input.data))
        self.tool_picker_prompt = self.tool_picker_prompt.get_prompt()

        tool_picker_pill = Pill(handler=input.handler, data=LLMInputSchema(query=self.tool_picker_prompt))
        self.llm.set_input_schema(new_schema=LLMInputSchema)
        self.llm.set_output_schema(new_schema=self.ToolPickerSchema)
        response = self.llm.run(input=tool_picker_pill)

        picked_tool = self.tool_picker_tool.run(response).data
        tool_name = picked_tool.chosen_tool
        tool_object = self.tool_objects[tool_name]

        self.job_worker_prompt.patch(tool_description=self.tools[tool_name], data=str(input.data))
        self.job_worker_prompt = self.job_worker_prompt.get_prompt()

        job_worker_pill = Pill(handler=input.handler, data=LLMInputSchema(query=self.job_worker_prompt))
        self.llm.set_input_schema(new_schema=LLMInputSchema)
        self.llm.set_output_schema(new_schema=tool_object.input_schema)
        response = self.llm.run(input=job_worker_pill)
        result = tool_object.run(input=response)

        return result
        