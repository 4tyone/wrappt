# SiRe - Simulation Reasoning

# instead of chain-of-thought ot tree-of-thought the model tries to solve the task in "mind" by thinking and simulating the solution and then give out answer.

from wrappt.base import Pipeline, Pill
from wrappt.builtin.llm import LLM
from wrappt.builtin.pipelines.SiRe.prompts import SiRePrompt, SimulationPrompt
from wrappt.builtin.pipelines.SiRe.schemas import SiReOutputSchema, SimulationOutputSchema, SiReInputSchema

from pydantic import BaseModel

from typing import Optional


class SiRe(Pipeline):
    def __init__(self, llm: LLM, max_iterations: Optional[int] = -1, verbose: Optional[bool] = True, simulation_prompt: Optional[BaseModel] = SimulationPrompt, *args, **kwargs):
        input_schema = SiReInputSchema
        output_schema = SiReOutputSchema
        super().__init__(*args, **kwargs, input_schema=input_schema, output_schema=output_schema, llm=llm)
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.simulation_prompt = simulation_prompt

    def forward(self, input: Pill) -> Pill:
        thoughts_history = input.data.copy_history()
        thoughts_history.history_messages[-1]["content"] = str(SiRePrompt(query=thoughts_history.history_messages[-1]["content"]))
        simulation_history = input.data.copy_history()
        final_answer = True
        iteration = 0
        while final_answer or iteration < self.max_iterations:
            iteration += 1
            internal_response = self.llm.generate(messages=thoughts_history.get_history(), output_schema=self.output_schema)
            if internal_response.stage == "FinalAnswer":
                input.data.add_message(role="assistant", content=str(internal_response))
                return Pill(handler=input.handler, data=input.handler.handle_ok(internal_response))
            elif internal_response.stage == "Thought":
                thoughts_history.history_messages[-1]["content"] = thoughts_history.history_messages[-1]["content"] + f"\n\nStep {iteration}\n\n" + str(internal_response) 
            elif internal_response.stage == "Simulate":
                # TODO: SimulationPrompt(query= this needs to be the history not just the last message
                simulation_history.history_messages[-1]["content"] = str(self.simulation_prompt(query=simulation_history.history_messages[-1]["content"], solution=str(internal_response)))
                # TODO: delete this
                import time
                time.sleep(30)
                simulation_response = self.llm.generate(messages=simulation_history.get_history(), output_schema=SimulationOutputSchema)
                thoughts_history.history_messages[-1]["content"] = thoughts_history.history_messages[-1]["content"] + f"\n\nStep {iteration}\n\n" + str(simulation_response)
            else:
                return Pill(handler=input.handler, data=input.handler.handle_err(KeyError("No such stage, try one of Thought, Simulate or FinalAnswer.")))

            if self.verbose:
                pass
                print(thoughts_history)
                print(thoughts_history.history_messages[-1]["content"])