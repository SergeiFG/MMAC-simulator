from basics.parameter import PathLike, path_to_str, path_to_list, Timer
from typing import Any, Tuple

class StorageInterface:
    """
    Интерфейс для хранения параметров модели
    """
    
    def __init__(self):
        raise NotImplementedError("StorageInterface является абстрактным классом и не может быть инстанцирован напрямую")
    
    
    def read_values(self, paths: list[PathLike]) -> dict[PathLike, Any]:
        """
        Чтение значений параметров по списку путей

        Args:
            paths (list[PathLike]): Список путей к параметрам

        Returns:
            dict[PathLike, Any]: Словарь с путями и их значениями
        """
        raise NotImplementedError("Метод read_values должен быть реализован в подклассе")
    
    
    def write_values(self, values: dict[PathLike, Any]):
        """
        Запись значений параметров по словарю путей и значений

        Args:
            values (dict[PathLike, Any]): Словарь с путями и их значениями
        """
        raise NotImplementedError("Метод write_values должен быть реализован в подклассе")
    
    def read_history(self, path: list[PathLike], start_step: int = None, end_step: int = None) -> tuple[dict[PathLike, list[Any]], list[float]]:
        """
        Чтение истории значений параметров по пути или списку путей

        Args:
            path (PathLike | list[PathLike]): Путь или список путей к параметрам
            start_step (int, optional): Начальный шаг для чтения истории. Defaults to None.
            end_step (int, optional): Конечный шаг для чтения истории. Defaults to None.

        Returns:
            dict[PathLike, list[Any]]: Словарь с путями и их историей значений
            list[float]: Список временных меток для каждого шага
        """
        raise NotImplementedError("Метод read_history должен быть реализован в подклассе")
    
    def read_time(self, start_step: int = None, end_step: int = None) -> list[float]:
        """
        Чтение истории времени по шагам

        Args:
            start_step (int, optional): Начальный шаг для чтения времени. Defaults to None.
            end_step (int, optional): Конечный шаг для чтения времени. Defaults to None.

        Returns:
            list[float]: Список временных меток для каждого шага
        """
        raise NotImplementedError("Метод read_time должен быть реализован в подклассе")
    
    def advance_step(self, time: float):
        """
        Продвигает шаг симуляции на заданное время

        Args:
            time (float): Время для следующего шага
        """
        raise NotImplementedError("Метод advance_step должен быть реализован в подклассе") 
    
    def save_csv(self, path: str):
        """
        Сохраняет текущие значения параметров в CSV файл

        Args:
            path (str): Путь к файлу для сохранения
        """
        raise NotImplementedError("Метод save_csv должен быть реализован в подклассе")
    
    
class MemoryStorage(StorageInterface):
    """
    Класс для хранения параметров модели в памяти
    в формате {Pathlike: list[Any]} 
    
    """
    
    def __init__(self, first_time: float):
        """
        Создание хранилища в оперативной памяти
        """
        self.data: dict[PathLike, list[Any]] = {}
        self.time: list[float] = [first_time]
        self.step: int = 0
        

        
    def read_values(self, paths: list[PathLike]) -> dict[PathLike, Any]:
        """
        Чтение параметров из словаря по набору путей

        Args:
            paths (list[PathLike]): массив путей к параметрам

        Returns:
            dict[PathLike, Any]: словарь с путями и их значениями
        """
        paths = [path_to_str(p) for p in paths]
        return {p: self.data[p][-1] for p in paths if p in self.data}
    
    def write_values(self, values: dict[PathLike, Any]):
        """
        Записать данные в хранилище

        Args:
            values (dict[PathLike, Any]): словарь в формате путь - значение
        """
        
        for path, value in values.items():
            path_str = path_to_str(path)
            if path_str not in self.data:
                self.data[path_str] = [None] * (self.step + 1)  # Заполняем предыдущие шаги None
            self.data[path_str][self.step] = value
            
    def read_history(self, path: list[PathLike], start_step: int = 0, end_step: int = None) -> tuple[dict[PathLike, list[Any]], list[float]]:
        """
        Считывает историю изменений значений для выбранных параметров

        Args:
            path (list[PathLike]): массив путей к параметрам, которые нужно прочесть
            start_step (int, optional): С какого шага нужно начать чтение. Defaults to 0.
            end_step (int, optional): Последний шаг для чтения истории. По умолчанию последняя запись

        Returns:
            dict[PathLike, list[Any]]: словарь с историями массивов значений
            list[float]: массив временных меток
        """
        if end_step is None:
            end_step = self.step
            
        path_strs = [path_to_str(p) for p in path]
        history = {}
        
        for p in path_strs:
            if p in self.data:
                history[p] = self.data[p][start_step:end_step]
        
        return history, self.time[start_step:end_step]
    
    def read_time(self, start_step: int = 0, end_step: int = None) -> list[float]:
        """
        Чтение массива временных меток

        Args:
            start_step (int, optional): С какого шага нужно начать чтение. Defaults to 0.
            end_step (int, optional): Последний шаг для чтения истории. По умолчанию последняя запись
            
        Returns:
            list[float]: массив временных меток выбранного промежутка шагов
        """
        if end_step is None:
            end_step = self.step
        return self.time[start_step:end_step]

    def advance_step(self, time: float):        
        """
        свинуть шаг  для меток хранилища.
        Все параметры копируют предыдущее значение. Если новое не запишется, то останется таким.

        Args:
            time (float): новая временная метка
        """
        for path in self.data:
            self.data[path].append(self.data[path][-1])  # Заполняем последним значением для необновленных параметров
                    
        self.time.append(time)
        self.step += 1
        
    def save_csv(self, path: str):
        """
        Сохранение истории параметров в csv таблицу

        Args:
            path (str): путь для сохранения параметров
        """
        import pandas as pd
        
        # Создаем DataFrame из словаря
        df = pd.DataFrame(self.data)
        
        # Добавляем столбец времени
        df.insert(0, 'time', self.time)
        
        # Сохраняем в CSV
        df.to_csv(path, index=False)