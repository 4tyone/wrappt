from wrappt.base import Pipeline, Pill, Layer
from wrappt.builtin.llm import LLM
from wrappt.builtin.pipelines.JobWorker.prompts import ToolPickerPrompt, JobWorkerPrompt
from wrappt.builtin.pipelines.JobWorker.tools import ToolPickerTool, ChosenToolSchema
from typing import List, Dict, Type
from pydantic import BaseModel


class JobWorker(Pipeline):

    def __init__(self, llm: LLM, *args, **kwargs):
        super().__init__(*args, **kwargs, llm=llm, input_schema=ToolPickerPrompt)
        self.tools: Dict[str, str] = {}
        self.tool_objects: Dict[str, Layer] = {}

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
        