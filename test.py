from basics import Model, Parameter, MemoryStorage, Timer


class SubModel(Model):
    def __init__(self, name: str = "", parameters: dict[str, Parameter] = {}, timer: Timer = None):
        super().__init__(name, parameters, timer)
        self.param_out = Parameter(read = False)
        
    def calculate(self):
        self.param_out = self.time * 2

class TestModel(Model):
    def __init__(self, name: str, parameters: dict[str, Parameter] = {}, timer: Timer = None):
        super().__init__(name, parameters, timer)
        self.param_out = Parameter(value=0, read=False)
        self.param_in = Parameter(value=0, read=True, read_path="Model.param_out")
        self.param_delta = Parameter(value=2, read=False)
        self.param_out2 = Parameter(read = False)
        self.sub_model = SubModel()

    def calculate(self):
        self.param_out = self.param_in + self.param_delta
        self.param_out2 = -self.time
        self.sub_model.advance()

timer = Timer()        
model = TestModel(name="Model")
storage = MemoryStorage(first_time=timer.time)


model.set_storage(storage)
model.set_timer(timer)
model.inherit_path()

model.advance()
model.param_delta = 3
for i in range(5):
    timer(delta_time= 1)
    storage.advance_step(timer.time)
    model.advance()


print(f"params : {model.time, model.param_in, model.param_delta, model.param_out, model.param_out2}")
print(f"Submodel params: {model.sub_model.param_out}")

print(model.sub_model.__dict__)
print(model.sub_model.__dict__["param_out"].__dict__)

print(storage.data)
print(storage.time)
print(storage.step)

storage.save_csv(path="example.csv")
