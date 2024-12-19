# TODO: the idea is to give a task to an LLM and ask it to solve it, then take that solution and prompt the LLM again
# this time we ask it to find what's wrong with the answer and fix it
# Repeat this process N times and give out the final answer
# or implement an early stop mechanism by asking the LLM if the task is solved correctly return done (or something like that)

from wrappt.base import Pipeline, Pill
from wrappt.builtin.llm import LLM


class PingPong(Pipeline):
    llm: LLM