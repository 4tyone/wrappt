from wrappt.base import Pipeline, Pill

class Sequential(Pipeline): #TODO: This will not work, needs to be fixed
    def forward(self, input: Pill) -> Pill:
        x = input
        for layer in self.layers:
            x = layer.run(x)

        return x