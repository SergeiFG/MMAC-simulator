from typing import List, Literal, Any, Union, TypeAlias
from numbers import Number

PathLike: TypeAlias = List[str] | str

def path_to_str(path: PathLike) -> str:
    """
    Преобразует путь в строку

    Args:
        path (PathLike): Путь к параметру

    Returns:
        str: Строковое представление пути
    """
    if isinstance(path, list):
        return ".".join(path)
    return path

def path_to_list(path: PathLike) -> List[str]:
    """
    Преобразует путь в список

    Args:
        path (PathLike): Путь к параметру

    Returns:
        List[str]: Список элементов пути
    """
    if isinstance(path, str):
        return path.split(".")
    return path

class Parameter:
    """
    Класс для описания параметров данной модели
    """
    
    def __init__(self, value: Number = None, read: bool = False, read_path: PathLike = None, limits: tuple[Number, Number] = [None, None]):
        """
        Инициализация параметра 

        Args:
            value (Number, optional): _description_. Defaults to None.
            read (bool, optional): _description_. Defaults to False.
            read_path (PathLike, optional): _description_. Defaults to None.
            limits (Union[Number, Number], optional): _description_. Defaults to [None, None].
        """
        self.limits = limits
        self.path: PathLike = [""]
        self.value = value
        self.read = read
        self.read_path = read_path
        
        
    def _check_limits(self):
        """
        Проверка что значение параметра находится в пределах допустимых значений
        """
        if self.limits[0] is not None:
            if self.value < self.limits[0]:
                raise ValueError(f"Value {self.value} is below the lower limit {self.limits[0]}")
        if self.limits[1] is not None:
            if self.value > self.limits[1]:
                raise ValueError(f"Value {self.value} is above the upper limit {self.limits[1]}")
                    
    def __call__(self, *args, **kwargs) -> "Parameter":
         return self
    
    def __setattr__(self, name, value):
        if name == "value":
            self.__dict__[name] = value
            self._check_limits()
        else:
            self.__dict__[name] = value
        

class Timer:
    """
    Класс для отслеживания времени в модели
    """    
    def __init__(self, time: float = 0.0):
        """
        Инициализация таймера

        Args:
            time (float, optional): Начальное время. Defaults to 0.0.
        """
        self.time = time
        
    def __call__(self, delta_time: float,*args, **kwargs) -> None:
        """
        Сдвигает время симуляции

        Args:
            delta_time (float): Дельта времени для следующего шага
        """
        self.time += delta_time
        
    
        
if __name__ == "__main__":
    param = Parameter(value=5, read=True, read_path="some.path", limits=[0, 10])
    print(f"Parameter value: {param.value}")
    print(f"Parameter read: {param.read}")
    print(f"Parameter read path: {param.read_path}")
    print(f"Parameter limits: {param.limits}")
    print(f"Accessing parameter value using __get__: {param}")
    print(param().__dict__)
    print("Limits check passed.")