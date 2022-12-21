from adapters import FluxAdapter, console


class CommandUpdate:

    def __init__(self):
        pass

    def execute(self, component):
        if component == "flux":
            self.update_flux()
        else:
            console.panic(f"I don't know how to update {component}")

    def update_flux(self):
        with console.status("Updating Flux"):
            self.flux = FluxAdapter()
            res = self.flux.bootstrap()

            if res.is_ok():
                console.success("Flux deployed successfully")
            else:
                console.panic("Failed deploying Flux", res.message)
