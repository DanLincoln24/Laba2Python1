
import unittest
import tempfile
import json
import os
from src.main import (
    Task, TaskSource, FileTaskSource,
    RandomTaskSource, ApiStubSource,
    process_tasks, safe_process
)

class Tests(unittest.TestCase):
    def test_1_task_creation(self):
        task = Task(id=42, payload="привет")
        self.assertEqual(task.id, 42)
        self.assertEqual(task.payload, "привет")

    def test_2_file_source_reads_tasks(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump([
                {"id": 1, "payload": "один"},
                {"id": 2, "payload": "два"}
            ], f)
            filename = f.name

        # Читаем задачи
        source = FileTaskSource(filename)
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, 1)
        self.assertEqual(tasks[0].payload, "один")
        self.assertEqual(tasks[1].id, 2)
        self.assertEqual(tasks[1].payload, "два")

        # Удаляем файл
        os.unlink(filename)

    def test_3_random_source_generates_correct_count(self):
        source = RandomTaskSource(5)
        tasks = list(source.get_tasks())
        self.assertEqual(len(tasks), 5)

    def test_4_api_source_returns_fixed_tasks(self):
        source = ApiStubSource("http://test.com")
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "api_1")
        self.assertEqual(tasks[1].id, "api_2")
        self.assertEqual(tasks[0].payload["source"], "stub")

    def test_5_all_sources_follow_protocol(self):
        sources = [
            FileTaskSource("test.json"),
            RandomTaskSource(3),
            ApiStubSource("http://test.com")
        ]

        for source in sources:
            self.assertIsInstance(source, TaskSource)
            self.assertTrue(hasattr(source, 'get_tasks'))
            self.assertTrue(callable(source.get_tasks))

    def test_6_safe_process_rejects_non_sources(self):
        not_sources = [
            "строка",
            123,
            [],
            {},
            None
        ]

        for bad_source in not_sources:
            # проверяем, что не падает с ошибкой
            try:
                safe_process(bad_source)
            except Exception:
                self.fail(f"safe_process упал с {bad_source}")

    def test_8_empty_json_file(self):
        # Создаём пустой JSON-файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[]')
            filename = f.name

        source = FileTaskSource(filename)
        tasks = list(source.get_tasks())

        assert len(tasks) == 0

        os.unlink(filename)

    def test_9_json_file_with_empty_strings(self):
        # Создаём файл с пустыми строками
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[{"id": 1, "payload": ""}]')
            filename = f.name

        source = FileTaskSource(filename)
        tasks = list(source.get_tasks())

        # Проверяем, что пустая строка сохраняется
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].payload == ""

        os.unlink(filename)

    def test_10_json_file_missing_fields(self):
        # Создаём файл без поля id
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[{"payload": "no id"}]')
            filename = f.name

        # Проверяем, что возникает ошибка KeyError
        source = FileTaskSource(filename)
        try:
            list(source.get_tasks())
            assert False, "Должна была возникнуть ошибка KeyError"
        except KeyError:
            pass

        os.unlink(filename)

    def test_11_random_source_zero_count(self):
        source = RandomTaskSource(0)
        tasks = list(source.get_tasks())
        assert len(tasks) == 0

    def test_12_random_source_negative_count(self):
        source = RandomTaskSource(-5)
        tasks = list(source.get_tasks())
        assert len(tasks) == 0  # range(-5) не даёт элементов

    def test_13_api_source_empty_payload(self):
        source = ApiStubSource("http://test.com")
        tasks = list(source.get_tasks())

        # Проверяем, что данные не пустые
        assert len(tasks) == 2
        assert tasks[0].payload != {}
        assert tasks[1].payload != {}

    def test_14_file_source_nonexistent_file(self):
        source = FileTaskSource("nevergonnagivyouup.json")
        try:
            list(source.get_tasks())
            assert False, "Должна была возникнуть ошибка FileNotFoundError"
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    unittest.main()