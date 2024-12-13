from wrappt.base import Pipeline, Pill, Layer
from wrappt.builtin.llm import LLM
from wrappt.builtin.prompts import ToolPickerPrompt, JobWorkerPrompt
from pydantic import create_model
from typing import List, Dict, Type
from pydantic import BaseModel


class ChosenToolSchema(BaseModel):
            chosen_tool: str

class ToolPickerTool(Layer):
    llm: LLM

    def _tool_picker_schema(self, name: str, tool_names: List[str]):
        """
        Create a Pydantic model where each field is a boolean.
        The LLM will decide which tool is True.
        """
        fields = {field_name: (bool, ...) for field_name in tool_names}
        Base = create_model(name, **fields)
        return Base

    @staticmethod
    def _tool_string_to_dict(input_string: str) -> Dict[str, str]:
        lines = input_string.strip().split("\n")
        
        result_dict = {}
        for line in lines:
            key, value = line.split(": ", 1)
            result_dict[key] = eval(value)
        
        return result_dict

    def run(self, input: Pill, tool_names: List[str]) -> Pill:
        self.pill_validator(pill=input)
        ToolPickerSchema = self._tool_picker_schema("ToolPickerSchema", tool_names=tool_names)
        response = self.llm.generate(input=input, output_schema=ToolPickerSchema)

        attributes = response.data.model_dump()
        if not all(isinstance(value, bool) for value in attributes.values()):
            return input.handler.handle_err(ValueError("All attributes must be boolean."))

        true_attributes = [key for key, value in attributes.items() if value]

        if len(true_attributes) == 0:
            return input.handler.handle_err(ValueError("At least one attribute must be True."))
        elif len(true_attributes) > 1:
            return input.handler.handle_err(ValueError("Only one attribute must be True."))

        chosen_tool = input.handler.handle_ok(true_attributes[0])
        return Pill(handler=input.handler, data=self.output_schema(chosen_tool=chosen_tool))
  

class JobWorker(Pipeline):
    input_schema: Type[BaseModel] = ToolPickerPrompt

    def __init__(self, layers: List[Layer], output_schema: Type[BaseModel], llm: LLM):
        super().__init__(layers=layers, output_schema=output_schema)
        self.tools: Dict[str, str] = {}
        self.tool_objects: Dict[str, Layer] = {}
        self.llm: LLM = llm

        for layer in self.layers:
            self.tools[layer.name] = layer.context
            self.tool_objects[layer.name] = layer
  
        self.tool_picker_tool = ToolPickerTool(
            name="tool_picker_tool",
            context="This tool returns the correct tool that the LLM chooses",
            llm=self.llm,
            input_schema=self.input_schema,
            output_schema=ChosenToolSchema,
        )

    def forward(self, input: Pill) -> Pill:
        tool_picker_prompt: BaseModel = self.input_schema(tool_names_and_descriptions="\n    " + "\n".join(f"{key}: {value}" for key, value in self.tools.items()), data=str(input.data))
        tool_picker_pill: Pill = Pill(handler=input.handler, data=tool_picker_prompt)
        picked_tool: ChosenToolSchema = self.tool_picker_tool.run(input=tool_picker_pill, tool_names=list(self.tools.keys())).data
        
        tool_name: str = picked_tool.chosen_tool
        tool_object: Layer = self.tool_objects[tool_name]

        job_worker_prompt: BaseModel = JobWorkerPrompt(tool_description=self.tools[tool_name], data=str(input.data))

        job_worker_pill: Pill = Pill(handler=input.handler, data=job_worker_prompt)

        result: Pill = tool_object.run(input=job_worker_pill)

        return result
        