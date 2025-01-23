# TODO: ReAct agent based on JobWorker pipeline

from wrappt.base import Pipeline, Pill
from wrappt.builtin.llm import LLM

class ReAct(Pipeline):
    llm: LLM

    