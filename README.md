<p align="center">
  <img src="wrappt.png" alt="Wrappt" width="200"/>
  <h1 align="center">Wrappt</h1>
</p>

<p align="center">
  Wrappt is a minimalistic LLM wrapper framework designed for production and centered around robust error handling.
</p>

<p align="center">
  <a href="https://github.com/4tyone/wrappt/blob/dev/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT" title="MIT License" />
  </a>
  <a href="https://discord.gg/GaadFrx2">
    <img src="https://img.shields.io/discord/1258658826257961020" alt="Discord" title="Discord" />
  </a>
  

</p>

---

## The philosophy

Wrappt philosophy is simple, you get a headache while using it because you are forced to handle the errors before your code can do anything even remotely useful, BUT in return you get a headacheless rest of your life after deploying you application. Countless times I received a call about my application failing on a friday night, and when I get into the logs and look at the code I realize that it is because of a stupid exception that I never new can occur and never handled it in the first place. Wrappt solves this by moving out all of your error handling procedures into a centralized, easy to manage place. On top of that it forces you to handle an error if the function you are using can throw an error, in short if a function/method can throw an error, you will be forced to handle it before you can use it.

## Pill

All building blocks of Wrappt are written in the base.py file, and the most notable one is the Pill class. The Pill is something where you put your data into before passing into a function/method. To construct a Pill you need to input a Handler object and BaseModel object (from pydantic). You need to inherit the Handler interface and implement it's two methods - handle_ok and handle_err. Handler goes into the Pill and is passed to the function where it can call the handle_err on errors when they occur and it will handle them, also call handle_ok on ok values.

python```
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


```

