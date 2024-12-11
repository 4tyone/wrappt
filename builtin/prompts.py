from wrappt.base import Prompt


tool_picker_prompt = Prompt(prompt_schema={
                    "task": ("You will be given a query and some additional data about a task that needs to be performed."
                            "You have several tool names and their descriptions under your disposal, your job is to match the correct tool to the job."
                            "For each tool return True or False, if True that tool is the correct one to use, there can only be one True, the rest are False."),
                    "data": None,
                    "tool_names_and_descriptions": None,
                })

job_worker_prompt = Prompt(prompt_schema={
                    "task": ("You are given a tool with it's description and a query that you need to perform with that tool."
                             "Read the query and all available data given to you and generate a proper request that will be sent to the tool."),
                    "tool_description": None,
                    "data": None,
                })