from dataclasses import dataclass
from typing import Iterable, Any, Protocol, runtime_checkable
import json
import random
import string

@dataclass
class Task:
    id: int | str
    payload: Any

@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[Task]:
        ...

class FileTaskSource:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def get_tasks(self) -> Iterable[Task]:
        with open(self.filename) as f:
            data = json.load(f)
        for item in data:
            yield Task(id=item['id'], payload=item['payload'])

class RandomTaskSource:
    def __init__(self, count: int) -> None:
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(self.count):
            yield Task(
                id=i,
                payload=''.join(random.choices(string.ascii_letters, k=5))
            )

class ApiStubSource:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_tasks(self) -> Iterable[Task]:
        return [
            Task(id='api_1', payload={'source': 'stub', 'data': 'value1'}),
            Task(id='api_2', payload={'source': 'stub', 'data': 'value2'}),
        ]

def process_tasks(source: TaskSource) -> None:
    for task in source.get_tasks():
        print(f"  → Задача {task.id}: {task.payload}")

def safe_process(source: object) -> None:
    if isinstance(source, TaskSource):
        print(f"\nОбработка источника: {source.__class__.__name__}")
        process_tasks(source)
    else:
        print(f"Объект {source} не является источником задач (контракт не соблюдён)")

if __name__ == "__main__":
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tf:
        json.dump([
            {"id": 1, "payload": "file task 1"},
            {"id": 2, "payload": "file task 2"}
        ], tf)
        temp_filename = tf.name

    file_source = FileTaskSource(temp_filename)
    random_source = RandomTaskSource(3)
    api_source = ApiStubSource("https://example.com/api")

    safe_process(file_source)
    safe_process(random_source)
    safe_process(api_source)
    safe_process("not a source")