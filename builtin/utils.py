from wrappt.base import Handler

def sequential_builder():
    # TODO: implement
    pass

def handle_err_builder(handler: Handler):
    # TODO: analyzes the handler you give to it and finds every usage and every kind of error inputed into handle_err 
    # and builds a match-case based handler for every kind of error object
    # this needs to be a wrappt cli command
    # one idea is to make a decorator for the handle_err of a specific Handler object that will mark it so that the CLI tool will know which handler to build
    pass