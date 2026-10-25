Версия 3 среды имитационного моделирования для MMAC. 
Отличия:
- Максимально упрощённые правила определения моделей и параметров
- Общее хранилище данных
- Глобальный таймер симуляции и общий доступ к временной метке

## Текущие значения и история

```python
model.param_out                       # текущее значение
model.param_out = 10                   # обновить текущее значение
model["param_out"].path                # метаданные объекта Parameter

model.history.param_out               # список сохранённых значений
model.history["param_out"]             # то же, если имя задано строкой
model.history.param_out[-1]            # последнее сохранённое значение
model.history.param_out[-3:]           # последние три значения
model.history.time                    # временные метки сохранённых шагов

model.sub_model.history.param_out     # история параметра подмодели
model.history.sub_model.param_out     # тот же результат
```

Для чтения диапазона непосредственно из хранилища:

```python
model.read_history("param_out", start_step=1, end_step=4)
model.read_history(model["param_out"], start_step=-3)
```

Границы работают как срезы списка Python: начало включается, конец исключается;
отрицательные индексы отсчитываются с конца. Без границ возвращаются все записи,
включая начальный и текущий сохранённый шаг.

Перед чтением истории нужно подключить хранилище через `set_storage()` и настроить
пути параметров через `inherit_path()`. Например:

```python
from basics import Model, Parameter, MemoryStorage, Timer

timer = Timer()
model = Model("Model", parameters={"speed": Parameter(value=5)})
storage = MemoryStorage(first_time=timer.time)
model.set_timer(timer)
model.set_storage(storage)
model.inherit_path()
model.write_parameters()

timer.advance(1)
storage.advance_step(timer.time)
model.speed = 8
model.write_parameters()

print(model.speed)                     # 8
print(model.history.speed)             # [5, 8]
print(model.history.time)              # [0.0, 1.0]
```

История содержит значения, записанные через `write_parameters()` (в том числе
внутри `advance()`). Само присваивание `model.speed = 8` не записывает историю.
Повторная запись на одном шаге обновляет его значение; новый шаг создаётся вызовом
`storage.advance_step(...)` и до записи переносит предыдущие значения.

Каждое обращение к истории возвращает свежий список. Изменение этого списка не
меняет хранилище; присваивать значения через `model.history.speed = ...` нельзя.
У ещё не записанного параметра история пуста, а у впервые записанного на позднем
шаге предыдущие позиции заполнены `None`. Для входных параметров (`read=True`)
история читается по собственному `path`, а не по `read_path` источника.

