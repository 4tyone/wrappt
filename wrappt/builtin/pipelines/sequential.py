from wrappt.base import Pipeline, Pill

class Sequential(Pipeline):
    def forward(self, input: Pill) -> Pill:
        x = input
        for layer in self.layers:
            layer.pill_validator(x)
            x = layer.run(x)

        return x