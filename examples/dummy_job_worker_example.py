from wrappt.builtin.llm import LLMInputSchema, Pill
from wrappt.base import Handler, Layer
from wrappt.builtin.pipelines.JobWorker.job_worker import JobWorker, LLM

from pydantic import BaseModel
from typing import Any


class CodeReaderSchema(BaseModel):
    file_path: str
    start_line: int
    end_line: int

class GotoDefinition(BaseModel):
    file_path: str
    line: int
    entity: str

class ReturnSchema(BaseModel):
    result: str

class SomeHandler(Handler):
    def handle_ok(self, *args: Any, **kwargs: Any):
        if len(args) == 1 and not kwargs:
            return args[0]
        
        if args and not kwargs:
            return args
        
        if not args and kwargs:
            return kwargs
        
        return args, kwargs

    def handle_err(self, error: Exception):
        match error:
            case ValueError():
                return "A ValueError occurred: " + str(error)
            
class GotoDefinitionTool(Layer):
    def run(self, input: Pill) -> Pill:
        print(self.llm.generate(input=input, output_schema=GotoDefinition).data)
        return_obj = ReturnSchema(result="No definition found")
        return Pill(handler=input.handler, data=return_obj)
    
class CodeReaderTool(Layer):
    def run(self, input: Pill) -> Pill:
        print(self.llm.generate(input=input, output_schema=CodeReaderSchema).data)
        return_obj = ReturnSchema(result="No codes found")
        return Pill(handler=input.handler, data=return_obj)


claude = LLM(context="You are an assistant with tools.",
             provider="anthropic",
             model="claude-3-5-sonnet-20241022",
             api_key="",
             )

# claude = LLM(context="You are an assistant with tools.",
#              provider="ollama",
#              model="deepseek-coder-v2",
#              api_key="",
#              )

# claude = LLM(context="You are an assistant with tools.",
#              provider="deepseek",
#              model="deepseek-chat",
#              api_key="",
#              )

code_reader_tool = CodeReaderTool(name="code_reader_tool",
                                  context=("code_reader_tool is useful when you need to read code of a certain line range in a specific file."
                                            "Given the file path and line range this will return the code written in that file in that line range."
                                            "Each line also states the lane number in the beginning like so - '2: ', notice the space, be careful when reading the indentation."
                                            "Write file_path, end_line, start_line and their values as is, don't wrap with quatation marks."),
                                  llm=claude,
                                  input_schema=CodeReaderSchema,
                                  output_schema=ReturnSchema)

goto_definition_tool = GotoDefinitionTool(name="goto_definition_tool",
                                          context=("This tool is useful when you want to see the definition of an entity (like a function call)."
                                                   "Given the file path, the line and the entity this tool will give you the definition of that entity with a doc string, if available."
                                                   ),
                                          llm=claude,
                                          input_schema=GotoDefinition,
                                          output_schema=ReturnSchema)

layers = [code_reader_tool, goto_definition_tool]


job_worker_pill = Pill(handler=SomeHandler(), data=LLMInputSchema(query="Read the file at location C://User//text.txt"))

snek_pipeline = JobWorker(layers=layers, output_schema=ReturnSchema, llm=claude)

print(snek_pipeline.forward(input=job_worker_pill).data)


