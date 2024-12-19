from pydantic import create_model


ToolPickerPrompt = create_model("ToolPickerPrompt",
                                task = (str, ("You will be given a query and some additional data about a task that needs to be performed."
                                              "You have several tool names and their descriptions under your disposal, your job is to match the correct tool to the job."
                                              "Return the tool name that you think is a good fit to use for the task.")),
                                data = (str, ...),
                                tool_names_and_descriptions = (str, ...))

JobWorkerPrompt = create_model("JobWorkerPrompt",
                                task = (str, ("You are given a tool with it's description and a query that you need to perform with that tool."
                                              "Read the query and all available data given to you and generate a proper request that will be sent to the tool.")),
                                tool_description = (str, ...),
                                data = (str, ...))