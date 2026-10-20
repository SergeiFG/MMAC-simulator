from basics.parameter import Parameter, PathLike, path_to_str, path_to_list, Timer
from basics.storage import StorageInterface

class Model:
    
    def __init__(self, name:str = "", parameters: dict[str, Parameter] = {}, timer: Timer = None):
        self.name = name
        self.path = [name]
        self.timer = timer
        self.time = None
        self.storage: StorageInterface = None
        for param_name, param in parameters.items():
            self.__dict__[param_name] = param
            
            
    
    def __getitem__(self, key):
        """
        Возврат значения. При обращении к Parameter возвращает его value

        Args:
            key (_type_): требуемое поле

        Returns:
            _type_: value параметра, если он является экземпляром Parameter, иначе возвращает сам объект
        """
        if isinstance(self.__dict__[key], Parameter):
            return self.__dict__[key].value
        if key == "time":
            return self.timer.time if self.timer else None
        return self.__dict__[key]
    
    def __getattribute__(self, name):
        """
        Возврат значения. При обращении к Parameter возвращает его value

        Args:
            name (_type_): требуемое поле

        Returns:
            _type_: value параметра, если он является экземпляром Parameter, иначе возвращает сам объект
        """

        attribute = object.__getattribute__(self, name)
        if isinstance(attribute, Parameter):
            return attribute.value
        if name == "time":
            return self.timer.time if self.timer else None
        return attribute

    def __setattr__(self, name, value):
        """Обновляет value существующего Parameter, сохраняя сам параметр."""
        attribute = object.__getattribute__(self, "__dict__").get(name)
        if isinstance(attribute, Parameter):
            attribute.value = value
        else:
            object.__setattr__(self, name, value)
    
    def __setitem__(self, key, value):
        """
        Для Parameter устанавливает значение в value, для остальных элементов работает как обычно

        Args:
            key (_type_): требуемое поле
            value (_type_): значение для установки
        """
        if not isinstance(self.__dict__[key], Parameter):
            self.__dict__[key] = value
        else:
            self.__dict__[key].value = value
            
    def inherit_path(self, parent_path: PathLike = []):
        """
        Устанавливает путь для всех параметров модели, наследуя путь от родительской модели

        Args:
            parent_path (PathLike): Путь родительской модели
        """
        self.path = path_to_list(parent_path) + [self.name]
        for param_name, param in self.__dict__.items():
            if isinstance(param, Parameter):
                param.path = self.path + [param_name]
            
            if isinstance(param, Model):
                param.name =param_name
                param.inherit_path(parent_path=self.path)
                
    def set_storage(self, storage: StorageInterface):
        """
        Устанавливает интерфейс для хранения параметров модели

        Args:
            storage (StorageInterface): Интерфейс для хранения параметров модели
        """
        self.storage = storage
        
        for param_name, param in self.__dict__.items():
            if isinstance(param, Model):
                param.set_storage(storage)
                
    def set_timer(self, timer: Timer):
        """
        Устанавливает таймер для модели

        Args:
            timer (Timer): Таймер для модели
        """
        self.timer = timer
        
        for param_name, param in self.__dict__.items():
            if isinstance(param, Model):
                param.set_timer(timer)
                
    def read_parameters(self):
        """
        Читает значения параметров модели из хранилища
        """
        if self.storage is None:
            raise ValueError("Storage is not set. Please set storage using set_storage method.")
        
        params_paths = {path_to_str(param.read_path): param_name for param_name, param in self.__dict__.items() if isinstance(param, Parameter) and param.read}
        paths_to_read = params_paths.keys()
        
        read_values = self.storage.read_values(paths_to_read)
        
        for key, value in read_values.items():
            self.__dict__[params_paths[key]].value = value
        
        for param_name, param in self.__dict__.items():
            if isinstance(param, Model):
                param.read_parameters()
                
    def write_parameters(self):
        """
        Записывает значения параметров модели в хранилище
        """
        if self.storage is None:
            raise ValueError("Storage is not set. Please set storage using set_storage method.")
        
        params_paths = {path_to_str(param.path): param_name for param_name, param in self.__dict__.items() if isinstance(param, Parameter)}
        values_to_write = {path_to_str(path): self.__dict__[param_name].value for path, param_name in params_paths.items()}
        
        self.storage.write_values(values_to_write)
        
        for param_name, param in self.__dict__.items():
            if isinstance(param, Model):
                param.write_parameters()
    
    def advance(self):
        """
        Метод для продвижении шага симуляции
        """
        self.read_parameters()
        self.calculate()
        self.write_parameters()
        
    def calculate(self):
        """
        Метод для вычисления внутренней логики модели

        """
        raise NotImplementedError("Метод должен быть определён в конкретной имплементации модели")    
        
if __name__ == "__main__":

    param1 = Parameter(value=5, read=True, read_path="param1", limits=[0, 10])
    param2 = Parameter(value=15, read=False, read_path="param2", limits=[10, 20])
    model = Model(name="TestModel", parameters={"param1": param1, "param2": param2})
    model.param3 = Parameter(value=False)
    
    model.inherit_path()
    
    print(f"Model path: {model.path}")
    print(f"Param1 path: {param1.path}, value: {model.param1}")
    print(f"Param2 path: {param2.path}, value: {model.param2}")
    param3 = model.__dict__["param3"]
    print(f"Param3 path: {param3.path}, value: {model.param3}")
    print(f"Accessing param : {param3.__dict__}")
    model.param3 = True
    model.param2 = 18
    model.param1 = -5
    print(f"Accessing param : {param3.__dict__}")
    print(f" Параметры модели: {model.param1}, {model.param2}, {model.param3}")
    
